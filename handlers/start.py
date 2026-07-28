from telegram import Update
from telegram.ext import ContextTypes

from services.quiz import ensure_default_quiz_setting


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    welcome_text = (
        "🎓 *Welcome to Study Helper AI*\n\n"
        "मैं आपका AI Study Assistant हूँ।\n\n"
        "✨ मैं आपकी मदद कर सकता हूँ:\n"
        "📚 पढ़ाई में\n"
        "📝 नोट्स बनाने में\n"
        "❓ सवाल हल करने में\n"
        "🧠 Concepts समझाने में\n"
        "📅 Daily Quiz देने में\n\n"
        "Daily Quiz अब by default ON रहेगा.\n"
        "शुरू करने के लिए कोई भी सवाल भेजें या /quiz लिखें।"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
    )

    if user:
        await ensure_default_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
