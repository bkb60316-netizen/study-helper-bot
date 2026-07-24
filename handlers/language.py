from telegram import Update
from telegram.ext import ContextTypes


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌐 *Language Settings*\n\n"
        "अभी bot इन languages को समझ सकता है:\n"
        "• हिंदी\n"
        "• English\n\n"
        "Future में हम और languages जोड़ेंगे।\n"
        "अगर तुम चाहो, तो आगे इसमें language switch button भी जोड़ देंगे।"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
