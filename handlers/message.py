import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.ai_router import generate_response
from services.history import save_chat_history
from services.intent import detect_intent, is_greeting
from services.logger import logger
from services.memory import get_recent_chat_history
from services.quiz import (
    compute_next_run_at,
    ensure_default_quiz_setting,
    save_quiz_setting,
)
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

    # quiz topic input
    if context.user_data.get("awaiting_quiz_topic"):
        context.user_data.pop("awaiting_quiz_topic", None)
        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            quiz_topic=user_message,
        )
        await update.message.reply_text(
            f"📚 Quiz topic set to: {user_message}"
        )
        return

    # quiz time input
    if context.user_data.get("awaiting_quiz_time"):
        try:
            quiz_time = user_message.replace(" ", "")
            # normalize_quiz_time is inside services.quiz but not imported here yet
            from services.quiz import normalize_quiz_time  # local import to avoid cycle

            quiz_time = normalize_quiz_time(quiz_time)
        except Exception:
            await update.message.reply_text(
                "Please send time in HH:MM format.\nExample: 20:30"
            )
            return

        context.user_data.pop("awaiting_quiz_time", None)

        setting = await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            quiz_time=quiz_time,
        )

        if setting.get("enabled"):
            next_run_at = compute_next_run_at(quiz_time)
            await save_quiz_setting(
                telegram_user_id=user.id,
                next_run_at=next_run_at,
            )

        await update.message.reply_text(
            f"⏰ Quiz time set to {quiz_time} IST."
        )
        return

    await ensure_default_quiz_setting(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    if is_greeting(user_message):
        try:
            reply_text = await generate_response(
                user_text=(
                    "Reply with a short, warm greeting and ask the user "
                    "to send a study question."
                ),
                intent="chat",
                history=[],
                preferred_language_instruction=profile["instruction"],
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
            preferred_language_instruction=profile["instruction"],
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
