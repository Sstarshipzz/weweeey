from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import uuid

class AdminHandler:
    def __init__(self, bot):
        self.bot = bot

    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu d'administration"""
        # Vérifier si l'utilisateur est admin
        if update.effective_user.id not in self.bot.admin_ids:
            if update.callback_query:
                await update.callback_query.message.edit_text("⛔️ Accès non autorisé")
            else:
                await update.message.reply_text("⛔️ Accès non autorisé")
            return
    
        # Préparer le message
        message_text = (
            "*👑 MENU ADMINISTRATION*\n\n"
            "Choisissez une action :"
        )
    
        # Si c'est un callback (bouton cliqué)
        if update.callback_query:
            await update.callback_query.message.edit_text(
                message_text,
                reply_markup=self.bot.keyboard_manager.get_admin_keyboard(),
                parse_mode='Markdown'
            )
        # Si c'est une commande /admin
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=self.bot.keyboard_manager.get_admin_keyboard(),
                parse_mode='Markdown'
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les callbacks admin"""
        query = update.callback_query
        await query.answer()

        print(f"Admin callback reçu: {query.data}")  # Debug log

        try:
            if query.data == "admin_menu":
                await self.admin_menu(update, context)
            
            elif query.data == "admin_new_cat":
                context.user_data['creating_category'] = True
                await query.message.edit_text(
                    "🏷️ *Création d'une nouvelle catégorie*\n\n"
                    "Envoyez le nom de la catégorie :",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Annuler", callback_data="admin_menu")
                    ]])
                )

            elif query.data == "admin_new_prod":
                if not self.bot.catalog['categories']:
                    await query.message.edit_text(
                        "❌ Vous devez d'abord créer une catégorie.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("➕ Créer une catégorie", callback_data="admin_new_cat")
                        ]]),
                        parse_mode='Markdown'
                    )
                    return

                await query.message.edit_text(
                    "🆕 *Création d'un nouveau produit*\n\n"
                    "Sélectionnez la catégorie :",
                    reply_markup=self.bot.keyboard_manager.get_manage_products_keyboard(),
                    parse_mode='Markdown'
                )

            elif query.data.startswith("new_prod_cat_"):
                cat_id = query.data.split('_')[3]
                category = next(c for c in self.bot.catalog["categories"] if c["id"] == cat_id)
                context.user_data['creating_product'] = True
                context.user_data['product_data'] = {'category_id': cat_id}
                await query.message.edit_text(
                    f"📝 *Création d'un produit dans {category['name']}*\n\n"
                    f"Envoyez le nom du produit :",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Annuler", callback_data="admin_menu")
                    ]])
                )

            elif query.data == "admin_manage_cats":
                await self.manage_categories(update, context)

            elif query.data == "admin_manage_prods":
                await self.manage_products(update, context)

            elif query.data.startswith("del_cat_"):
                cat_id = query.data.split('_')[2]
                await self.delete_category(update, context, cat_id)

            elif query.data.startswith("del_prod_"):
                prod_id = query.data.split('_')[2]
                await self.delete_product(update, context, prod_id)

            elif query.data.startswith("admin_view_cat_"):
                cat_id = query.data.split('_')[3]
                await self.show_category_products(update, context, cat_id)
            
            else:
                print(f"Callback non géré: {query.data}")
            
        except Exception as e:
            print(f"Erreur dans handle_callback: {e}")
            await query.message.edit_text(
                "❌ Une erreur est survenue.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour au menu", callback_data="admin_menu")
                ]])
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les messages pour la création"""
        if not update.effective_user.id in self.bot.admin_ids:
            return

        print(f"État user_data: {context.user_data}")  # Debug log

        if context.user_data.get('creating_category'):
            print("Création catégorie en cours")  # Debug log
            await self.handle_category_creation(update, context)
        elif context.user_data.get('creating_product'):
            print("Création produit en cours")  # Debug log
            await self.handle_product_creation(update, context)

    async def handle_category_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la création d'une catégorie"""
        category_name = update.message.text
        category_id = f"cat_{str(uuid.uuid4())[:8]}"
        
        self.bot.catalog['categories'].append({
            "id": category_id,
            "name": category_name,
            "description": f"Catégorie {category_name}"
        })
        
        self.bot.save_catalog()
        context.user_data.clear()
        
        await update.message.reply_text(
            f"✅ Catégorie *{category_name}* créée avec succès!",
            parse_mode='Markdown'
        )

    async def create_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initialise la création d'un produit"""
        if not self.bot.catalog['categories']:
            await update.callback_query.message.edit_text(
                "❌ Vous devez d'abord créer une catégorie.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("➕ Créer une catégorie", callback_data="admin_new_cat")
                ]]),
                parse_mode='Markdown'
            )
            return

        await update.callback_query.message.edit_text(
            "🆕 *Création d'un nouveau produit*\n\n"
            "Sélectionnez la catégorie :",
            reply_markup=self.bot.keyboard_manager.get_manage_products_keyboard(),
            parse_mode='Markdown'
        )

    async def manage_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Affiche la liste des catégories avec options de suppression"""
        await update.callback_query.message.edit_text(
            "*🗂️ GÉRER LES CATÉGORIES*\n\n"
            "Cliquez sur 🗑️ pour supprimer une catégorie\n"
            "⚠️ La suppression supprimera aussi tous les produits associés",
            reply_markup=self.bot.keyboard_manager.get_manage_categories_keyboard(),
            parse_mode='Markdown'
        )

    async def manage_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Affiche la liste des catégories pour gérer les produits"""
        await update.callback_query.message.edit_text(
            "*📦 GÉRER LES PRODUITS*\n\n"
            "Choisissez une catégorie :",
            reply_markup=self.bot.keyboard_manager.get_manage_products_keyboard(),
            parse_mode='Markdown'
        )

    async def show_category_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE, cat_id: str):
        """Affiche les produits d'une catégorie pour gestion"""
        try:
            category = next(c for c in self.bot.catalog["categories"] if c["id"] == cat_id)
            products = [p for p in self.bot.catalog["products"] if p["category_id"] == cat_id]
        
            await update.callback_query.message.edit_text(
                f"*📦 PRODUITS DE {category['name'].upper()}*\n\n"
                f"Cliquez sur 🗑️ pour supprimer un produit",
                reply_markup=self.bot.keyboard_manager.get_manage_category_products_keyboard(cat_id),
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Erreur dans show_category_products: {e}")
            await update.callback_query.message.edit_text(
                "❌ Une erreur est survenue.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour", callback_data="admin_manage_cats")
                ]])
            )

    async def handle_product_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la création d'un produit"""
        product_data = context.user_data.get('product_data', {})
        
        if 'category_id' in product_data:
            if 'name' not in product_data:
                product_data['name'] = update.message.text
                context.user_data['product_data'] = product_data
                await update.message.reply_text(
                    "📝 Maintenant, envoyez la description du produit :"
                )
                return
                
            elif 'description' not in product_data:
                product_data['description'] = update.message.text
                context.user_data['product_data'] = product_data
                await update.message.reply_text(
                    "💰 Envoyez le prix du produit (exemple: 99.99) :"
                )
                return
                
            elif 'price' not in product_data:
                try:
                    price = float(update.message.text.replace(',', '.'))
                    product_data['price'] = price
                    context.user_data['product_data'] = product_data
                    await update.message.reply_text(
                        "📸 Envoyez une photo ou vidéo du produit\n"
                        "ou tapez 'skip' pour passer cette étape"
                    )
                except ValueError:
                    await update.message.reply_text("❌ Prix invalide. Réessayez (exemple: 99.99):")

    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la réception des médias pour les produits"""
        if not update.effective_user.id in self.bot.admin_ids:
            return

        if context.user_data.get('creating_product'):
            product_data = context.user_data.get('product_data', {})
            
            if update.message.photo:
                product_data['media_id'] = update.message.photo[-1].file_id
                product_data['media_type'] = 'photo'
            elif update.message.video:
                product_data['media_id'] = update.message.video.file_id
                product_data['media_type'] = 'video'
            
            # Créer le produit
            product_id = f"prod_{str(uuid.uuid4())[:8]}"
            self.bot.catalog['products'].append({
                "id": product_id,
                "category_id": product_data['category_id'],
                "name": product_data['name'],
                "description": product_data['description'],
                "price": product_data['price'],
                "media_id": product_data.get('media_id'),
                "media_type": product_data.get('media_type')
            })
            
            self.bot.save_catalog()
            context.user_data.clear()
            
            await update.message.reply_text(
                f"✅ Produit *{product_data['name']}* créé avec succès!",
                parse_mode='Markdown'
            )

    async def delete_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, cat_id: str):
        """Supprime une catégorie"""
        print(f"Suppression catégorie {cat_id}")  # Debug log
        try:
            # Trouver la catégorie
            category = next(c for c in self.bot.catalog["categories"] if c["id"] == cat_id)
            
            # Supprimer les produits
            self.bot.catalog['products'] = [p for p in self.bot.catalog['products'] 
                                          if p['category_id'] != cat_id]
            
            # Supprimer la catégorie
            self.bot.catalog['categories'] = [c for c in self.bot.catalog['categories'] 
                                            if c['id'] != cat_id]
            
            self.bot.save_catalog()
            print("Catégorie supprimée avec succès")  # Debug log
            
            await update.callback_query.message.edit_text(
                f"✅ Catégorie *{category['name']}* supprimée avec succès.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour", callback_data="admin_manage_cats")
                ]])
            )
        except Exception as e:
            print(f"Erreur suppression catégorie: {e}")  # Debug log
            await update.callback_query.message.edit_text(
                "❌ Erreur lors de la suppression de la catégorie.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour", callback_data="admin_manage_cats")
                ]])
            )

    async def delete_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prod_id: str):
        """Supprime un produit"""
        print(f"Suppression produit {prod_id}")  # Debug log
        try:
            # Trouver le produit
            product = next(p for p in self.bot.catalog["products"] if p["id"] == prod_id)
            cat_id = product['category_id']
            
            # Supprimer le produit
            self.bot.catalog['products'] = [p for p in self.bot.catalog['products'] 
                                          if p['id'] != prod_id]
            
            self.bot.save_catalog()
            print("Produit supprimé avec succès")  # Debug log
            
            await update.callback_query.message.edit_text(
                f"✅ Produit *{product['name']}* supprimé avec succès.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour", callback_data=f"manage_prods_cat_{cat_id}")
                ]])
            )
        except Exception as e:
            print(f"Erreur suppression produit: {e}")  # Debug log
            await update.callback_query.message.edit_text(
                "❌ Erreur lors de la suppression du produit.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Retour", callback_data="admin_manage_prods")
                ]])
            )