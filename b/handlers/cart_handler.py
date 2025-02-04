# handlers/cart_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from typing import Dict

class Cart:
    def __init__(self):
        self.items = {}  # product_id: quantity
        self.last_updated = datetime.utcnow()

    def add_item(self, product_id: str, quantity: int = 1):
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity
        self.last_updated = datetime.utcnow()

    def remove_item(self, product_id: str, quantity: int = 1):
        if product_id in self.items:
            self.items[product_id] = max(0, self.items[product_id] - quantity)
            if self.items[product_id] == 0:
                del self.items[product_id]
            self.last_updated = datetime.utcnow()

    def clear(self):
        self.items.clear()
        self.last_updated = datetime.utcnow()

    def get_total(self, catalog) -> float:
        total = 0
        for product_id, quantity in self.items.items():
            product = next(p for p in catalog["products"] if p["id"] == product_id)
            total += product["price"] * quantity
        return total

class CartHandler:
    def __init__(self, bot):
        self.bot = bot
        self.user_carts: Dict[int, Cart] = {}

    def get_user_cart(self, user_id: int) -> Cart:
        """Récupère ou crée le panier d'un utilisateur"""
        if user_id not in self.user_carts:
            self.user_carts[user_id] = Cart()
        return self.user_carts[user_id]

    def format_cart_message(self, cart: Cart) -> str:
        """Formate le message du panier"""
        if not cart.items:
            return (
                "*🛒 PANIER*\n\n"
                "Votre panier est vide.\n\n"
                "_Parcourez notre catalogue pour ajouter des produits !_"
            )

        message = "*🛒 PANIER*\n\n"
        total = 0

        for product_id, quantity in cart.items.items():
            product = next(p for p in self.bot.catalog["products"] if p["id"] == product_id)
            subtotal = product["price"] * quantity
            total += subtotal
            message += (
                f"• {product['name']}\n"
                f"  └ {quantity}× {product['price']}€ = {subtotal:.2f}€\n\n"
            )

        message += f"\n💰 *Total :* {total:.2f}€"
        return message

    def get_cart_keyboard(self, cart: Cart) -> InlineKeyboardMarkup:
        """Crée le clavier pour le panier"""
        keyboard = []
        
        # Boutons pour chaque produit
        for product_id in cart.items:
            product = next(p for p in self.bot.catalog["products"] if p["id"] == product_id)
            keyboard.append([
                InlineKeyboardButton(f"➖ {product['name']}", callback_data=f"remove_{product_id}"),
                InlineKeyboardButton(f"➕", callback_data=f"add_{product_id}")
            ])

        # Boutons de navigation
        nav_buttons = []
        if cart.items:
            nav_buttons = [
                [InlineKeyboardButton("🗑️ Vider le panier", callback_data="clear_cart")],
                [InlineKeyboardButton("💳 Commander", callback_data="checkout")]
            ]
        
        nav_buttons.append([
            InlineKeyboardButton("📚 CATALOGUE", callback_data="catalog"),
            InlineKeyboardButton("🏠 MENU", callback_data="menu")
        ])
        
        keyboard.extend(nav_buttons)
        return InlineKeyboardMarkup(keyboard)

    async def handle_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère l'affichage du panier"""
        user_id = update.effective_user.id
        cart = self.get_user_cart(user_id)
        
        message = self.format_cart_message(cart)
        query = update.callback_query

        if query:
            await query.message.edit_text(
                message,
                reply_markup=self.get_cart_keyboard(cart),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=self.get_cart_keyboard(cart),
                parse_mode='Markdown'
            )

    async def handle_add_to_cart(self, update: Update, product_id: str):
        """Gère l'ajout d'un produit au panier"""
        query = update.callback_query
        user_id = update.effective_user.id
        cart = self.get_user_cart(user_id)
        
        product = next(p for p in self.bot.catalog["products"] if p["id"] == product_id)
        
        if product["stock"] > 0:
            cart.add_item(product_id)
            await query.answer("✅ Produit ajouté au panier!")
        else:
            await query.answer("❌ Produit en rupture de stock!", show_alert=True)

    async def handle_remove_from_cart(self, update: Update, product_id: str):
        """Gère la suppression d'un produit du panier"""
        query = update.callback_query
        user_id = update.effective_user.id
        cart = self.get_user_cart(user_id)
        
        cart.remove_item(product_id)
        await self.handle_cart(update, None)
        await query.answer("✅ Produit retiré du panier!")

    async def handle_clear_cart(self, update: Update):
        """Gère le vidage du panier"""
        query = update.callback_query
        user_id = update.effective_user.id
        cart = self.get_user_cart(user_id)
        
        cart.clear()
        await self.handle_cart(update, None)
        await query.answer("✅ Panier vidé!")