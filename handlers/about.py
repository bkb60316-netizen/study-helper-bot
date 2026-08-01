from telegram import Update
from telegram.ext import ContextTypes

from services.ui_localizer import localize_ui_text
from services.user_settings import get_user_language_profile


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    preferred_instruction = None

    if user:
        profile = await get_user_language_profile(user.id)
        if profile:
            preferred_instruction = profile["instruction"]

    text = (
        "ℹ️ About Study Helper AI\n\n"
        "Study Helper AI is a smart study assistant built for students.\n"
        "It can help with explanations, notes, MCQs, daily quizzes, memory-based "
        "study support, and selected-language replies.\n\n"
        "Future features will include better memory, image solving, PDF notes, "
        "and a full learning dashboard."
    )

    if preferred_instruction:
        text = await localize_ui_text(text, preferred_instruction)

    await update.message.reply_text(text)
