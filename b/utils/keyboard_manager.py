from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardManager:
    def __init__(self, bot):
        self.bot = bot

    def get_main_keyboard(self):
        """Clavier du menu principal"""
        keyboard = [
            [InlineKeyboardButton("📚 CATALOGUE", callback_data="catalog")],
            [InlineKeyboardButton("❓ AIDE", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_categories_keyboard(self):
        """Clavier pour afficher les catégories"""
        keyboard = []
        categories = self.bot.catalog["categories"]
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(
                categories[i]["name"], 
                callback_data=f"category_{categories[i]['id']}"
            )]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(
                    categories[i + 1]["name"], 
                    callback_data=f"category_{categories[i + 1]['id']}"
                ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🏠 MENU", callback_data="menu")])
        return InlineKeyboardMarkup(keyboard)

    def get_products_keyboard(self, category_id: str):
        """Clavier pour afficher les produits d'une catégorie"""
        keyboard = []
        products = [p for p in self.bot.catalog["products"] if p["category_id"] == category_id]
        
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    f"🔍 {product['name']}", 
                    callback_data=f"product_{product['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("📚 CATALOGUE", callback_data="catalog"),
            InlineKeyboardButton("🏠 MENU", callback_data="menu")
        ])
        return InlineKeyboardMarkup(keyboard)

    def get_product_keyboard(self, product_id: str, category_id: str):
        """Clavier pour la fiche produit"""
        keyboard = []
        
        # Boutons de contact depuis la config
        for button in self.bot.config['contact_buttons']:
            keyboard.append([InlineKeyboardButton(button['text'], url=button['url'])])
        
        # Navigation
        keyboard.append([
            InlineKeyboardButton("◀️ Retour", callback_data=f"category_{category_id}"),
            InlineKeyboardButton("🏠 MENU", callback_data="menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    def get_admin_keyboard(self):
        """Clavier du menu admin"""
        keyboard = [
            [InlineKeyboardButton("➕ Nouvelle Catégorie", callback_data="admin_new_cat")],
            [InlineKeyboardButton("➕ Nouveau Produit", callback_data="admin_new_prod")],
            [InlineKeyboardButton("🗑️ Gérer Catégories", callback_data="admin_manage_cats")],
            [InlineKeyboardButton("🗑️ Gérer Produits", callback_data="admin_manage_prods")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_manage_categories_keyboard(self):
        """Clavier pour gérer les catégories"""
        keyboard = []
        for cat in self.bot.catalog['categories']:
            keyboard.append([
                # Changé category_ en admin_view_cat_ pour différencier
                InlineKeyboardButton(f"📁 {cat['name']}", callback_data=f"admin_view_cat_{cat['id']}"),
                InlineKeyboardButton("🗑️", callback_data=f"del_cat_{cat['id']}")
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin_menu")])
        return InlineKeyboardMarkup(keyboard)

    def get_manage_products_keyboard(self):
        """Clavier pour choisir la catégorie dont on veut gérer les produits"""
        keyboard = []
        for cat in self.bot.catalog['categories']:
            keyboard.append([
                # Changé le callback pour la création de produit
                InlineKeyboardButton(f"📁 {cat['name']}", callback_data=f"new_prod_cat_{cat['id']}")
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin_menu")])
        return InlineKeyboardMarkup(keyboard)

    def get_manage_category_products_keyboard(self, category_id: str):
        """Clavier pour gérer les produits d'une catégorie"""
        keyboard = []
        products = [p for p in self.bot.catalog["products"] if p["category_id"] == category_id]
    
        for prod in products:
            keyboard.append([
                # Changé product_ en admin_view_prod_ pour différencier
                InlineKeyboardButton(f"🏷️ {prod['name']}", callback_data=f"admin_view_prod_{prod['id']}"),
                InlineKeyboardButton("🗑️", callback_data=f"del_prod_{prod['id']}")
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin_manage_cats")])
        return InlineKeyboardMarkup(keyboard)

    def get_help_keyboard(self):
        """Clavier pour le menu d'aide"""
        return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 MENU", callback_data="menu")]])