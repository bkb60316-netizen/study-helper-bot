from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    welcome_text = (
        "🎓 *Welcome to Study Helper AI*\n\n"
        "मैं आपका AI Study Assistant हूँ।\n\n"
        "✨ मैं आपकी मदद कर सकता हूँ:\n"
        "📚 पढ़ाई में\n"
        "📝 नोट्स बनाने में\n"
        "❓ सवाल हल करने में\n"
        "🧠 Concepts समझाने में\n"
        "📸 Image से Question Solve करने में\n\n"
        "शुरू करने के लिए कोई भी सवाल भेजें।"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
    )
