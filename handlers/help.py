from telegram import Update
from telegram.ext import ContextTypes

from services.ui_localizer import localize_ui_text
from services.user_settings import get_user_language_profile


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    preferred_instruction = None

    if user:
        profile = await get_user_language_profile(user.id)
        if profile:
            preferred_instruction = profile["instruction"]

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

    if preferred_instruction:
        help_text = await localize_ui_text(help_text, preferred_instruction)

    await update.message.reply_text(help_text)
