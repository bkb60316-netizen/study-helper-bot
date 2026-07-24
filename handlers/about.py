from telegram import Update
from telegram.ext import ContextTypes


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *About Study Helper AI*\n\n"
        "Study Helper AI एक smart study assistant है।\n"
        "यह आपको पढ़ाई में मदद करने के लिए बनाया गया है।\n\n"
        "✨ Future features:\n"
        "• AI Doubt Solver\n"
        "• Notes Generator\n"
        "• MCQ Generator\n"
        "• Image Question Solver\n"
        "• Daily Quiz\n"
        "• Study History\n"
        "• Multi-language Support\n"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
