from telegram import Update
from telegram.ext import ContextTypes

from services.quiz import get_quiz_setting
from services.user_settings import get_user_language_profile


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_language = "Not selected"

    if user:
        profile = await get_user_language_profile(user.id)
        if profile:
            current_language = profile["native_name"]

    text = (
        "⚙️ Settings\n\n"
        f"Current language: {current_language}\n"
        "Daily quiz: enabled by default after language selection\n"
        "Daily quiz time: 8:00 PM IST by default\n"
        "You can change your language anytime with /language\n"
        "More settings will be added later."
    )

    await update.message.reply_text(text)
