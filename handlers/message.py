import asyncio

from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes

from services.ai_router import generate_response
from services.history import save_chat_history
from services.intent import detect_intent, is_greeting
from services.logger import logger
from services.memory import get_recent_chat_history
from services.quiz import ensure_default_quiz_setting


MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🤖 AI Assistant"), KeyboardButton("📅 Daily Quiz")],
        [KeyboardButton("📚 My History"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("ℹ️ Help"), KeyboardButton("🌐 Language")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
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

    await ensure_default_quiz_setting(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    menu_text = user_message.lower()

    if user_message == "📅 Daily Quiz":
        setting = await context.application.bot_data.get("quiz_status_handler", None) if False else None
        await update.message.reply_text(
            "📅 Daily Quiz\n\n"
            "Quiz by default ON है.\n"
            "आप चाहें तो /quiz लिखकर settings देख सकते हैं."
        )
        return

    if user_message == "🤖 AI Assistant":
        await update.message.reply_text(
            "🤖 AI Assistant ready.\n\n"
            "अपना study question भेजो."
        )
        return

    if user_message == "📚 My History":
        await update.message.reply_text(
            "📚 History feature अभी next step में जोड़ेंगे."
        )
        return

    if user_message == "⚙️ Settings":
        await update.message.reply_text(
            "⚙️ Settings के लिए /settings use करो.",
            reply_markup=MENU_KEYBOARD,
        )
        return

    if user_message == "ℹ️ Help":
        await update.message.reply_text(
            "ℹ️ Help के लिए /help use करो.",
            reply_markup=MENU_KEYBOARD,
        )
        return

    if user_message == "🌐 Language":
        await update.message.reply_text(
            "🌐 Language के लिए /language use करो.",
            reply_markup=MENU_KEYBOARD,
        )
        return

    if is_greeting(user_message):
        reply_text = (
            "👋 Hello!\n\n"
            "मैं Study Helper AI हूँ।\n"
            "आप अपना कोई भी Study Question पूछ सकते हैं।"
        )
        await update.message.reply_text(reply_text, reply_markup=MENU_KEYBOARD)
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

    await update.message.reply_text(ai_reply, reply_markup=MENU_KEYBOARD)

    await save_chat_history(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        user_message=user_message,
        bot_reply=ai_reply,
        intent=intent,
    )
