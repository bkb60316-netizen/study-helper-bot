from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    help_text = (
        "📖 *Study Helper AI Help*\n\n"
        "/start - Bot शुरू करें\n"
        "/help - सहायता देखें\n\n"
        "आप मुझसे किसी भी विषय का सवाल पूछ सकते हैं।\n"
        "जल्द ही और भी फीचर्स जोड़े जाएंगे।"
    )

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )
