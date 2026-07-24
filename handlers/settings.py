from telegram import Update
from telegram.ext import ContextTypes


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚙️ *Settings*\n\n"
        "अभी basic version चल रहा है।\n\n"
        "Soon we will add:\n"
        "• Language switch\n"
        "• Daily quiz\n"
        "• Study history\n"
        "• AI mode selection\n"
        "• Privacy options\n"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
