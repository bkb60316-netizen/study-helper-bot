from telegram import Update
from telegram.ext import ContextTypes

from services.ai_router import generate_response
from services.intent import detect_intent, is_greeting
from services.logger import logger


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    user_message = update.message.text.strip()

    logger.info(f"Message Received: {user_message}")

    if is_greeting(user_message):
        await update.message.reply_text(
            "👋 Hello!\n\n"
            "मैं Study Helper AI हूँ।\n"
            "आप अपना कोई भी Study Question पूछ सकते हैं।"
        )
        return

    intent = detect_intent(user_message)

    try:
        ai_reply = await generate_response(user_message, intent=intent)
    except Exception as exc:
        logger.exception(f"AI response failed: {exc}")
        ai_reply = (
            "⚠️ अभी AI जवाब नहीं दे पाया।\n\n"
            "थोड़ी देर बाद फिर कोशिश करें।"
        )

    await update.message.reply_text(ai_reply)
