from telegram import Update
from telegram.ext import ContextTypes

from services.quiz import (
    build_quiz_difficulty_keyboard,
    build_quiz_status_keyboard,
    build_quiz_status_text,
    build_quiz_time_keyboard,
    build_quiz_time_prompt,
    build_quiz_topic_prompt,
    compute_next_run_at,
    disable_quiz_for_user,
    enable_quiz_for_user,
    generate_quiz_text_for_user,
    get_quiz_setting,
    normalize_difficulty,
    normalize_quiz_time,
    save_quiz_history,
    save_quiz_setting,
)
from services.user_settings import (
    build_language_keyboard,
    build_language_prompt_text,
    get_user_language_profile,
)


async def _show_quiz_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None or update.message is None:
        return

    setting = await get_quiz_setting(user.id)
    text = build_quiz_status_text(setting)
    keyboard = build_quiz_status_keyboard(setting)

    await update.message.reply_text(text, reply_markup=keyboard)


async def _edit_quiz_panel(query, user_id: int) -> None:
    setting = await get_quiz_setting(user_id)
    text = build_quiz_status_text(setting)
    keyboard = build_quiz_status_keyboard(setting)

    try:
        await query.edit_message_text(text, reply_markup=keyboard)
    except Exception:
        await query.message.reply_text(text, reply_markup=keyboard)


async def quiz_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    profile = await get_user_language_profile(user.id)

    if profile is None:
        await update.message.reply_text(
            build_language_prompt_text(),
            reply_markup=build_language_keyboard(),
        )
        return

    await _show_quiz_panel(update, context)


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or not query.data:
        return

    if not query.data.startswith("quiz:"):
        return

    await query.answer()

    user = query.from_user
    if user is None:
        return

    profile = await get_user_language_profile(user.id)
    if profile is None:
        await query.message.reply_text(
            build_language_prompt_text(),
            reply_markup=build_language_keyboard(),
        )
        return

    data = query.data

    if data == "quiz:refresh":
        await _edit_quiz_panel(query, user.id)
        return

    if data == "quiz:back":
        await _edit_quiz_panel(query, user.id)
        return

    if data == "quiz:toggle":
        setting = await get_quiz_setting(user.id)
        enabled = not bool(setting.get("enabled")) if setting else True

        if enabled:
            setting = await enable_quiz_for_user(
                telegram_user_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )
        else:
            setting = await disable_quiz_for_user(
                telegram_user_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )

        await _edit_quiz_panel(query, user.id)
        return

    if data == "quiz:time_menu":
        await query.edit_message_text(
            "⏰ Choose quiz time:",
            reply_markup=build_quiz_time_keyboard(),
        )
        return

    if data == "quiz:time_custom":
        context.user_data["awaiting_quiz_time"] = True
        context.user_data.pop("awaiting_quiz_topic", None)
        await query.message.reply_text(build_quiz_time_prompt())
        return

    if data.startswith("quiz:time:"):
        time_value = data.split("quiz:time:", 1)[1].strip()

        try:
            quiz_time = normalize_quiz_time(time_value)
        except ValueError as exc:
            await query.message.reply_text(str(exc))
            return

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

        await _edit_quiz_panel(query, user.id)
        return

    if data == "quiz:topic":
        context.user_data["awaiting_quiz_topic"] = True
        context.user_data.pop("awaiting_quiz_time", None)
        await query.message.reply_text(build_quiz_topic_prompt())
        return

    if data == "quiz:difficulty_menu":
        await query.edit_message_text(
            "🎯 Choose difficulty:",
            reply_markup=build_quiz_difficulty_keyboard(),
        )
        return

    if data.startswith("quiz:difficulty:"):
        difficulty_value = data.split("quiz:difficulty:", 1)[1].strip()

        try:
            difficulty = normalize_difficulty(difficulty_value)
        except ValueError as exc:
            await query.message.reply_text(str(exc))
            return

        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            difficulty=difficulty,
        )

        await _edit_quiz_panel(query, user.id)
        return

    if data == "quiz:now":
        setting = await get_quiz_setting(user.id)
        quiz_topic = (setting or {}).get("quiz_topic", "All subjects")
        difficulty = (setting or {}).get("difficulty", "easy")

        try:
            quiz_text = await generate_quiz_text_for_user(
                telegram_user_id=user.id,
                quiz_topic=quiz_topic,
                difficulty=difficulty,
                preferred_language_instruction=profile["instruction"],
            )
        except Exception:
            await query.message.reply_text("⚠️ अभी quiz generate नहीं हो पाया.")
            return

        await query.message.reply_text(quiz_text)

        await save_quiz_history(
            telegram_user_id=user.id,
            quiz_topic=quiz_topic,
            difficulty=difficulty,
            quiz_text=quiz_text,
        )
        return
