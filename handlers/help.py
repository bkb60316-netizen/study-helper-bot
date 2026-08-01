from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Study Helper AI Help\n\n"
        "/start - Start the bot\n"
        "/help - View this help\n"
        "/about - About this bot\n"
        "/language - Choose or change your study language\n"
        "/settings - View your current settings\n"
        "/quiz - Daily quiz controls\n\n"
        "Before you choose a language, I will only show the language picker.\n"
        "After you choose one, AI replies and quizzes will follow that language."
    )

    await update.message.reply_text(help_text)
