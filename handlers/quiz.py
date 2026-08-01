from telegram import Update
from telegram.ext import ContextTypes

from services.quiz import (
    build_quiz_status_text,
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
from services.ui_localizer import localize_ui_text
from services.user_settings import (
    build_language_keyboard,
    build_language_prompt_text,
    get_user_language_profile,
)


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

    args = context.args or []
    action = args[0].lower() if args else "status"

    setting = await get_quiz_setting(user.id)
    preferred_instruction = profile["instruction"]

    if action in {"help", "status"}:
        text = build_quiz_status_text(setting)
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action in {"on", "enable", "start"}:
        setting = await enable_quiz_for_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )

        text = (
            "✅ Daily quiz enabled.\n\n"
            f"Time: {setting.get('quiz_time', '20:00')} IST\n"
            f"Topic: {setting.get('quiz_topic', 'All subjects')}"
        )
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action in {"off", "disable", "stop"}:
        await disable_quiz_for_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )

        text = "🛑 Daily quiz disabled."
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action == "time":
        if len(args) < 2:
            text = "Use: /quiz time 20:30"
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
            return

        try:
            quiz_time = normalize_quiz_time(args[1])
        except ValueError as exc:
            text = str(exc)
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
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

        text = f"⏰ Quiz time set to {quiz_time} IST."
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action == "topic":
        if len(args) < 2:
            text = "Use: /quiz topic Physics"
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
            return

        topic = " ".join(args[1:]).strip()

        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            quiz_topic=topic,
        )

        text = f"📚 Quiz topic set to: {topic}"
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action in {"difficulty", "level"}:
        if len(args) < 2:
            text = "Use: /quiz difficulty easy"
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
            return

        try:
            difficulty = normalize_difficulty(args[1])
        except ValueError as exc:
            text = str(exc)
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
            return

        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            difficulty=difficulty,
        )

        text = f"🎯 Quiz difficulty set to: {difficulty}"
        text = await localize_ui_text(text, preferred_instruction)
        await update.message.reply_text(text)
        return

    if action == "now":
        quiz_topic = (setting or {}).get("quiz_topic", "All subjects")
        difficulty = (setting or {}).get("difficulty", "easy")

        try:
            quiz_text = await generate_quiz_text_for_user(
                telegram_user_id=user.id,
                quiz_topic=quiz_topic,
                difficulty=difficulty,
                preferred_language_instruction=preferred_instruction,
            )
        except Exception:
            text = "⚠️ अभी quiz generate नहीं हो पाया."
            text = await localize_ui_text(text, preferred_instruction)
            await update.message.reply_text(text)
            return

        await update.message.reply_text(quiz_text)

        await save_quiz_history(
            telegram_user_id=user.id,
            quiz_topic=quiz_topic,
            difficulty=difficulty,
            quiz_text=quiz_text,
        )
        return

    text = (
        "Use:\n"
        "/quiz status\n"
        "/quiz off\n"
        "/quiz time 20:30\n"
        "/quiz topic Physics\n"
        "/quiz difficulty medium\n"
        "/quiz now"
    )
    text = await localize_ui_text(text, preferred_instruction)
    await update.message.reply_text(text)
