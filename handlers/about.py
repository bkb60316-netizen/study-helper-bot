from telegram import Update
from telegram.ext import ContextTypes


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ About Study Helper AI\n\n"
        "Study Helper AI is a smart study assistant built for students.\n"
        "It can help with explanations, notes, MCQs, daily quizzes, memory-based "
        "study support, and selected-language replies.\n\n"
        "Future features will include better memory, image solving, PDF notes, "
        "and a full learning dashboard."
    )

    await update.message.reply_text(text)
