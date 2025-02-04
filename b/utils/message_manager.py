from telegram import Update
from telegram.ext import ContextTypes

class MessageManager:
    def __init__(self, bot):
        self.bot = bot

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère la commande /start"""
        user = update.effective_user
        welcome_message = (
            f"👋 *Bienvenue {user.first_name} !*\n\n"
            f"Je suis votre catalogue personnel.\n\n"
            f"*Que souhaitez-vous voir ?*\n"
            f"• 📚 Explorer le catalogue\n"
            f"• ❓ Obtenir de l'aide"
        )
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.bot.keyboard_manager.get_main_keyboard(),
            parse_mode='Markdown'
        )

    async def send_help(self, update: Update):
        """Envoie le message d'aide"""
        help_text = (
            "*❓ AIDE*\n\n"
            "Comment utiliser le bot :\n\n"
            "• 📚 *Catalogue :* Parcourez nos produits\n"
            "• 🔍 *Produit :* Cliquez sur un produit pour voir les détails\n"
            "• 💬 *Contact :* Utilisez les boutons sous chaque produit\n\n"
            "Pour toute question, contactez-nous via les boutons fournis."
        )
        await update.callback_query.message.edit_text(
            help_text,
            reply_markup=self.bot.keyboard_manager.get_help_keyboard(),
            parse_mode='Markdown'
        )

    async def send_error(self, update: Update, message: str):
        """Envoie un message d'erreur"""
        if update.callback_query:
            await update.callback_query.message.reply_text(
                f"❌ {message}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ {message}",
                parse_mode='Markdown'
            )

    async def send_success(self, update: Update, message: str):
        """Envoie un message de succès"""
        if update.callback_query:
            await update.callback_query.message.reply_text(
                f"✅ {message}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"✅ {message}",
                parse_mode='Markdown'
            )