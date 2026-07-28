import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.ai_router import generate_response
from services.history import save_chat_history
from services.intent import detect_intent, is_greeting
from services.logger import logger
from services.memory import get_recent_chat_history
from services.quiz import ensure_default_quiz_setting


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    if user is None:
        return

    user_message = update.message.text.strip()
    logger.info(f"Message Received: {user_message}")

    await ensure_default_quiz_setting(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    if is_greeting(user_message):
        reply_text = (
            "👋 Hello!\n\n"
            "मैं Study Helper AI हूँ।\n"
            "आप अपना कोई भी Study Question पूछ सकते हैं।"
        )
        await update.message.reply_text(reply_text)
        await save_chat_history(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            user_message=user_message,
            bot_reply=reply_text,
            intent="greeting",
        )
        return

    intent = detect_intent(user_message)
    memory = await asyncio.to_thread(get_recent_chat_history, user.id, 6)

    try:
        ai_reply = await generate_response(
            user_text=user_message,
            intent=intent,
            history=memory,
        )
    except Exception as exc:
        logger.exception(f"AI response failed: {exc}")
        ai_reply = (
            "⚠️ अभी AI जवाब नहीं दे पाया।\n\n"
            "थोड़ी देर बाद फिर कोशिश करें।"
        )

    await update.message.reply_text(ai_reply)

    await save_chat_history(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        user_message=user_message,
        bot_reply=ai_reply,
        intent=intent,
    )
