from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Study Helper AI Help*\n\n"
        "/start - Bot शुरू करें\n"
        "/help - सहायता देखें\n"
        "/about - About Study Helper AI\n"
        "/language - Language settings\n"
        "/settings - Bot settings\n"
        "/quiz - Daily quiz settings\n\n"
        "Quiz commands:\n"
        "/quiz on\n"
        "/quiz off\n"
        "/quiz time 20:30\n"
        "/quiz topic Physics\n"
        "/quiz difficulty medium\n"
        "/quiz now\n\n"
        "आप मुझसे किसी भी विषय का सवाल पूछ सकते हैं।"
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")
