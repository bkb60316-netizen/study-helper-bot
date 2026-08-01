from telegram import Update
from telegram.ext import ContextTypes

from services.quiz import ensure_default_quiz_setting
from services.ui_localizer import localize_ui_text
from services.user_settings import (
    build_language_keyboard,
    build_language_prompt_text,
    build_language_selected_text,
    get_language_profile,
    get_user_language_profile,
    set_user_language,
)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_language_name = None
    preferred_instruction = None

    if user:
        profile = await get_user_language_profile(user.id)
        if profile:
            preferred_instruction = profile["instruction"]
            current_language_name = profile["native_name"]

    prompt_text = build_language_prompt_text(current_language_name)

    if preferred_instruction:
        prompt_text = await localize_ui_text(prompt_text, preferred_instruction)

    await update.message.reply_text(
        prompt_text,
        reply_markup=build_language_keyboard(),
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or not query.data:
        return

    if not query.data.startswith("lang:"):
        return

    await query.answer()

    language_code = query.data.split(":", 1)[1].strip().lower()
    profile = get_language_profile(language_code)

    if profile is None:
        await query.edit_message_text(
            "⚠️ Unsupported language. Please try again with /language."
        )
        return

    user = query.from_user
    await set_user_language(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language_code=language_code,
    )

    await ensure_default_quiz_setting(
        telegram_user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    confirmation = build_language_selected_text(language_code)
    confirmation = await localize_ui_text(confirmation, profile["instruction"])

    try:
        await query.edit_message_text(confirmation)
    except Exception:
        await query.message.reply_text(confirmation)
