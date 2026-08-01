from telegram import Update
from telegram.ext import ContextTypes

from services.user_settings import (
    build_language_keyboard,
    get_user_language_profile,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_language_name = None

    if user:
        profile = await get_user_language_profile(user.id)
        if profile:
            current_language_name = profile["native_name"]

    welcome_text = (
        "🎓 Welcome to Study Helper AI\n\n"
        "I can help you with explanations, notes, MCQs, daily quizzes, "
        "and revision based on your chat history.\n\n"
        "Please choose the language you want to study in.\n"
        "After you choose one, I will reply only in that language."
    )

    if current_language_name:
        welcome_text += (
            f"\n\nCurrent language: {current_language_name}\n"
            "You can change it anytime with /language."
        )
    else:
        welcome_text += (
            "\n\nPlease choose your study language to continue."
        )

    await update.message.reply_text(
        welcome_text,
        reply_markup=build_language_keyboard(),
        )
