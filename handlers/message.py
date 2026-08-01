import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.ai_router import generate_response
from services.history import save_chat_history
from services.intent import detect_intent, is_greeting
from services.logger import logger
from services.memory import get_recent_chat_history
from services.user_settings import (
    build_language_keyboard,
    build_language_required_text,
    get_user_language_profile,
)


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

    profile = await get_user_language_profile(user.id)

    if profile is None:
        await update.message.reply_text(
            build_language_required_text(),
            reply_markup=build_language_keyboard(),
        )
        return

    preferred_language_instruction = profile["instruction"]

    if is_greeting(user_message):
        try:
            reply_text = await generate_response(
                user_text=(
                    "Reply with a short, warm greeting and ask the user "
                    "to send a study question."
                ),
                intent="chat",
                history=[],
                preferred_language_instruction=preferred_language_instruction,
            )
        except Exception as exc:
            logger.exception(f"Greeting generation failed: {exc}")
            reply_text = "Hello! Send me a study question."

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
            preferred_language_instruction=preferred_language_instruction,
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
