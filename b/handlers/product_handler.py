from telegram import Update
from telegram.ext import ContextTypes

class ProductHandler:
    def __init__(self, bot):
        self.bot = bot

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les callbacks liés aux produits"""
        query = update.callback_query
        await query.answer()

        if query.data == "catalog":
            await query.message.edit_text(
                "*📚 CATALOGUE*\n\n"
                "Choisissez une catégorie :",
                reply_markup=self.bot.keyboard_manager.get_categories_keyboard(),
                parse_mode='Markdown'
            )
            
        elif query.data == "menu":
            await query.message.edit_text(
                "*🏠 MENU PRINCIPAL*\n\n"
                "Que souhaitez-vous voir ?",
                reply_markup=self.bot.keyboard_manager.get_main_keyboard(),
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("category_"):
            category_id = query.data.split("_")[1]
            category = next(c for c in self.bot.catalog["categories"] if c["id"] == category_id)
            products = [p for p in self.bot.catalog["products"] if p["category_id"] == category_id]
            
            text = (
                f"*{category['name']}*\n\n"
                f"{category['description']}\n\n"
                f"📦 {len(products)} produits disponibles"
            )
            await query.message.edit_text(
                text,
                reply_markup=self.bot.keyboard_manager.get_products_keyboard(category_id),
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("product_"):
            await self.show_product(update)

        elif query.data == "help":
            await self.bot.message_manager.send_help(update)

    async def show_product(self, update: Update):
        """Affiche les détails d'un produit"""
        query = update.callback_query
        product_id = query.data.split("_")[1]
        product = next(p for p in self.bot.catalog["products"] if p["id"] == product_id)
        category = next(c for c in self.bot.catalog["categories"] if c["id"] == product["category_id"])
        
        price = "{:.2f}".format(product['price'])
        text = (
            f"*{product['name']}*\n\n"
            f"📝 *Description :*\n{product['description']}\n\n"
            f"💰 *Prix :* {price}€\n"
            f"🏷️ *Catégorie :* {category['name']}"
        )
        
        if product.get('media_id'):
            if product.get('media_type') == 'video':
                await query.message.reply_video(
                    video=product['media_id'],
                    caption=text,
                    reply_markup=self.bot.keyboard_manager.get_product_keyboard(product_id, product['category_id']),
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_photo(
                    photo=product['media_id'],
                    caption=text,
                    reply_markup=self.bot.keyboard_manager.get_product_keyboard(product_id, product['category_id']),
                    parse_mode='Markdown'
                )
            await query.message.delete()
        else:
            await query.message.edit_text(
                text,
                reply_markup=self.bot.keyboard_manager.get_product_keyboard(product_id, product['category_id']),
                parse_mode='Markdown'
            )