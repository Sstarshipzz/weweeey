import logging
from pathlib import Path
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from handlers.admin_handler import AdminHandler
from handlers.product_handler import ProductHandler
from utils.keyboard_manager import KeyboardManager
from utils.message_manager import MessageManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ShopBot:
    def __init__(self):
        # Charger la config et le catalogue
        self.config = self.load_config()
        self.catalog = self.init_catalog()
        self.admin_ids = self.config.get('admin_ids', [])

        # Initialiser les managers et handlers
        self.keyboard_manager = KeyboardManager(self)
        self.message_manager = MessageManager(self)
        self.admin_handler = AdminHandler(self)
        self.product_handler = ProductHandler(self)
        
        # Créer l'application
        self.app = Application.builder().token(self.config['bot_token']).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Configure les handlers du bot"""
        self.app.add_handler(CommandHandler("start", self.message_manager.start))
        self.app.add_handler(CommandHandler("admin", self.admin_handler.admin_menu))
    
        # Handler pour tous les types de messages texte
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.admin_handler.handle_message
        ))
    
        # Handler pour les médias
        self.app.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO,
            self.admin_handler.handle_media
        ))
    
        # Handler pour TOUS les callbacks
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Route les callbacks vers les bons handlers"""
        query = update.callback_query
        if query.data.startswith("admin_"):
            await self.admin_handler.handle_callback(update, context)
        else:
            await self.product_handler.handle_callback(update, context)

    def load_config(self):
        """Charge la configuration depuis config.json"""
        Path("config").mkdir(exist_ok=True)
        config_file = Path('config/config.json')
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "bot_token": "TON_TOKEN_ICI",
                "admin_ids": [],
                "contact_buttons": [
                    {
                        "text": "📱 Contact",
                        "url": "https://t.me/ton_username"
                    }
                ]
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            print("⚠️ Veuillez configurer config/config.json")
            exit(1)

    def init_catalog(self):
        """Initialise ou charge le catalogue"""
        Path("data").mkdir(exist_ok=True)
        catalog_file = Path('data/catalog.json')
        
        default_catalog = {
            "categories": [],
            "products": []
        }
        
        if not catalog_file.exists():
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(default_catalog, f, indent=4, ensure_ascii=False)
        
        with open(catalog_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_catalog(self):
        """Sauvegarde le catalogue dans le fichier"""
        with open('data/catalog.json', 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=4, ensure_ascii=False)

    def run(self):
        """Démarre le bot"""
        print("🤖 Bot démarré...")
        self.app.run_polling()

def main():
    bot = ShopBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        exit(1)

if __name__ == '__main__':
    main()