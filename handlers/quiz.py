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

    if action in {"help", "status"}:
        await update.message.reply_text(build_quiz_status_text(setting))
        return

    if action in {"on", "enable", "start"}:
        setting = await enable_quiz_for_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        await update.message.reply_text(
            "✅ Daily quiz enabled.\n\n"
            f"Time: {setting.get('quiz_time', '20:00')} IST\n"
            f"Topic: {setting.get('quiz_topic', 'All subjects')}"
        )
        return

    if action in {"off", "disable", "stop"}:
        await disable_quiz_for_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        await update.message.reply_text("🛑 Daily quiz disabled.")
        return

    if action == "time":
        if len(args) < 2:
            await update.message.reply_text("Use: /quiz time 20:30")
            return

        try:
            quiz_time = normalize_quiz_time(args[1])
        except ValueError as exc:
            await update.message.reply_text(str(exc))
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

        await update.message.reply_text(
            f"⏰ Quiz time set to {quiz_time} IST."
        )
        return

    if action == "topic":
        if len(args) < 2:
            await update.message.reply_text("Use: /quiz topic Physics")
            return

        topic = " ".join(args[1:]).strip()

        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            quiz_topic=topic,
        )

        await update.message.reply_text(
            f"📚 Quiz topic set to: {topic}"
        )
        return

    if action in {"difficulty", "level"}:
        if len(args) < 2:
            await update.message.reply_text("Use: /quiz difficulty easy")
            return

        try:
            difficulty = normalize_difficulty(args[1])
        except ValueError as exc:
            await update.message.reply_text(str(exc))
            return

        await save_quiz_setting(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            difficulty=difficulty,
        )

        await update.message.reply_text(
            f"🎯 Quiz difficulty set to: {difficulty}"
        )
        return

    if action == "now":
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
            await update.message.reply_text(
                "⚠️ अभी quiz generate नहीं हो पाया."
            )
            return

        await update.message.reply_text(quiz_text)

        await save_quiz_history(
            telegram_user_id=user.id,
            quiz_topic=quiz_topic,
            difficulty=difficulty,
            quiz_text=quiz_text,
        )
        return

    await update.message.reply_text(
        "Use:\n"
        "/quiz status\n"
        "/quiz off\n"
        "/quiz time 20:30\n"
        "/quiz topic Physics\n"
        "/quiz difficulty medium\n"
        "/quiz now"
    )
