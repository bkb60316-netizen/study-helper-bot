import asyncio
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from telegram.ext import Application, ContextTypes

from services.ai_router import generate_response
from services.database import database
from services.logger import logger
from services.memory import get_recent_chat_history
from services.user_settings import get_user_language_profile

IST = ZoneInfo("Asia/Kolkata")

DEFAULT_QUIZ_ENABLED = True
DEFAULT_QUIZ_TIME = "20:00"
DEFAULT_QUIZ_TOPIC = "All subjects"
DEFAULT_DIFFICULTY = "easy"

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def normalize_quiz_time(value: str) -> str:
    cleaned = (value or "").strip()
    match = _TIME_RE.match(cleaned)
    if not match:
        raise ValueError("Invalid time format. Use HH:MM like 20:30.")

    hour = int(match.group(1))
    minute = int(match.group(2))

    if hour > 23 or minute > 59:
        raise ValueError("Invalid time value. Use 00:00 to 23:59.")

    return f"{hour:02d}:{minute:02d}"


def normalize_difficulty(value: str) -> str:
    cleaned = (value or "").strip().lower()

    aliases = {
        "e": "easy",
        "easy": "easy",
        "आसान": "easy",
        "m": "medium",
        "medium": "medium",
        "मध्यम": "medium",
        "h": "hard",
        "hard": "hard",
        "कठिन": "hard",
    }

    if cleaned not in aliases:
        raise ValueError("Difficulty must be easy, medium, or hard.")

    return aliases[cleaned]


def compute_next_run_at(
    quiz_time: str,
    from_dt_utc: datetime | None = None,
) -> datetime:
    current_utc = from_dt_utc or datetime.now(timezone.utc)
    current_ist = current_utc.astimezone(IST)

    normalized_time = normalize_quiz_time(quiz_time)
    hour, minute = map(int, normalized_time.split(":"))

    candidate_ist = current_ist.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    if candidate_ist <= current_ist:
        candidate_ist += timedelta(days=1)

    return candidate_ist.astimezone(timezone.utc)


def _fetch_setting_sync(telegram_user_id: int) -> dict | None:
    client = database.get_client()
    response = (
        client.table("daily_quiz_settings")
        .select("*")
        .eq("telegram_user_id", telegram_user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def _save_setting_sync(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
    enabled: bool | None = None,
    quiz_time: str | None = None,
    quiz_topic: str | None = None,
    difficulty: str | None = None,
    next_run_at: datetime | None = None,
) -> dict:
    client = database.get_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    existing = _fetch_setting_sync(telegram_user_id)

    if existing:
        payload = {
            "username": username if username is not None else existing.get("username"),
            "first_name": first_name if first_name is not None else existing.get("first_name"),
            "enabled": enabled if enabled is not None else existing.get("enabled", DEFAULT_QUIZ_ENABLED),
            "quiz_time": quiz_time if quiz_time is not None else existing.get("quiz_time", DEFAULT_QUIZ_TIME),
            "quiz_topic": quiz_topic if quiz_topic is not None else existing.get("quiz_topic", DEFAULT_QUIZ_TOPIC),
            "difficulty": difficulty if difficulty is not None else existing.get("difficulty", DEFAULT_DIFFICULTY),
            "next_run_at": (
                next_run_at.isoformat()
                if next_run_at is not None
                else existing.get("next_run_at")
            ),
            "updated_at": now_iso,
        }

        client.table("daily_quiz_settings").update(payload).eq(
            "telegram_user_id", telegram_user_id
        ).execute()

        return _fetch_setting_sync(telegram_user_id) or payload

    payload = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "first_name": first_name,
        "enabled": enabled if enabled is not None else DEFAULT_QUIZ_ENABLED,
        "quiz_time": quiz_time or DEFAULT_QUIZ_TIME,
        "quiz_topic": quiz_topic or DEFAULT_QUIZ_TOPIC,
        "difficulty": difficulty or DEFAULT_DIFFICULTY,
        "next_run_at": next_run_at.isoformat() if next_run_at else None,
        "last_sent_for_date": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    client.table("daily_quiz_settings").insert(payload).execute()
    return _fetch_setting_sync(telegram_user_id) or payload


def _ensure_default_setting_sync(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> dict:
    existing = _fetch_setting_sync(telegram_user_id)
    if existing:
        return existing

    next_run_at = compute_next_run_at(DEFAULT_QUIZ_TIME)

    return _save_setting_sync(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        enabled=True,
        quiz_time=DEFAULT_QUIZ_TIME,
        quiz_topic=DEFAULT_QUIZ_TOPIC,
        difficulty=DEFAULT_DIFFICULTY,
        next_run_at=next_run_at,
    )


def _list_due_settings_sync(now_utc_iso: str) -> list[dict]:
    client = database.get_client()
    response = (
        client.table("daily_quiz_settings")
        .select("*")
        .eq("enabled", True)
        .lte("next_run_at", now_utc_iso)
        .execute()
    )
    return response.data or []


def _save_quiz_history_sync(
    telegram_user_id: int,
    quiz_topic: str,
    difficulty: str,
    quiz_text: str,
) -> None:
    client = database.get_client()
    payload = {
        "telegram_user_id": telegram_user_id,
        "quiz_topic": quiz_topic,
        "difficulty": difficulty,
        "quiz_text": quiz_text,
    }
    client.table("quiz_history").insert(payload).execute()


async def get_quiz_setting(telegram_user_id: int) -> dict | None:
    return await asyncio.to_thread(_fetch_setting_sync, telegram_user_id)


async def ensure_default_quiz_setting(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> dict:
    return await asyncio.to_thread(
        _ensure_default_setting_sync,
        telegram_user_id,
        username,
        first_name,
    )


async def save_quiz_setting(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
    enabled: bool | None = None,
    quiz_time: str | None = None,
    quiz_topic: str | None = None,
    difficulty: str | None = None,
    next_run_at: datetime | None = None,
) -> dict:
    return await asyncio.to_thread(
        _save_setting_sync,
        telegram_user_id,
        username,
        first_name,
        enabled,
        quiz_time,
        quiz_topic,
        difficulty,
        next_run_at,
    )


async def enable_quiz_for_user(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> dict:
    setting = await get_quiz_setting(telegram_user_id)
    quiz_time = (setting or {}).get("quiz_time", DEFAULT_QUIZ_TIME)
    next_run_at = compute_next_run_at(quiz_time)

    return await save_quiz_setting(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        enabled=True,
        next_run_at=next_run_at,
    )


async def disable_quiz_for_user(
    telegram_user_id: int,
    username: str | None = None,
    first_name: str | None = None,
) -> dict:
    return await save_quiz_setting(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        enabled=False,
    )


async def generate_quiz_text_for_user(
    telegram_user_id: int,
    quiz_topic: str,
    difficulty: str,
    preferred_language_instruction: str = "English",
) -> str:
    memory = await asyncio.to_thread(get_recent_chat_history, telegram_user_id, 8)

    recent_user_topics: list[str] = []
    for item in memory:
        if item.get("role") == "user":
            text = (item.get("content") or "").strip()
            if text:
                recent_user_topics.append(text)

    recent_context = (
        "\n".join(recent_user_topics[-5:])
        if recent_user_topics
        else "No recent study context available."
    )

    prompt = (
        f"Create a daily quiz for a student.\n"
        f"Primary Topic: {quiz_topic}\n"
        f"Difficulty: {difficulty}\n\n"
        f"User's recent study chat context:\n{recent_context}\n\n"
        "Rules:\n"
        "- Make the quiz mainly from the user's recent study chats.\n"
        "- If recent chats clearly point to a subject/topic, focus on that topic.\n"
        "- If recent chats are mixed, create a quiz from the most important study topic.\n"
        "- Generate exactly 5 multiple-choice questions.\n"
        "- Provide options A, B, C, D for each question.\n"
        "- Give the answer key at the end.\n"
        "- Keep language simple and student-friendly.\n"
        "- Do not mention that you used chat history.\n"
        "- Keep the output clean and easy to read.\n"
    )

    return await generate_response(
        prompt,
        intent="quiz",
        history=memory,
        preferred_language_instruction=preferred_language_instruction,
    )


async def save_quiz_history(
    telegram_user_id: int,
    quiz_topic: str,
    difficulty: str,
    quiz_text: str,
) -> None:
    try:
        await asyncio.to_thread(
            _save_quiz_history_sync,
            telegram_user_id,
            quiz_topic,
            difficulty,
            quiz_text,
        )
    except Exception as exc:
        logger.warning(f"Could not save quiz history: {exc}")


def build_quiz_status_text(setting: dict | None) -> str:
    if not setting:
        return (
            "📅 Daily Quiz\n\n"
            "This will be enabled by default after language selection.\n\n"
            "Commands:\n"
            "/quiz off\n"
            "/quiz time 20:00\n"
            "/quiz topic Physics\n"
            "/quiz difficulty medium\n"
            "/quiz now"
        )

    enabled = "ON" if setting.get("enabled") else "OFF"
    quiz_time = setting.get("quiz_time", DEFAULT_QUIZ_TIME)
    quiz_topic = setting.get("quiz_topic", DEFAULT_QUIZ_TOPIC)
    difficulty = setting.get("difficulty", DEFAULT_DIFFICULTY)
    next_run_at = setting.get("next_run_at") or "Not scheduled"

    return (
        "📅 Daily Quiz Status\n\n"
        f"Status: {enabled}\n"
        f"Time: {quiz_time} IST\n"
        f"Topic: {quiz_topic}\n"
        f"Difficulty: {difficulty}\n"
        f"Next Run: {next_run_at}\n\n"
        "Commands:\n"
        "/quiz off\n"
        "/quiz time HH:MM\n"
        "/quiz topic <topic>\n"
        "/quiz difficulty easy|medium|hard\n"
        "/quiz now"
    )


async def send_due_quizzes(context: ContextTypes.DEFAULT_TYPE) -> None:
    now_utc = datetime.now(timezone.utc)
    due_rows = await asyncio.to_thread(_list_due_settings_sync, now_utc.isoformat())

    if not due_rows:
        return

    for row in due_rows:
        telegram_user_id = int(row["telegram_user_id"])
        quiz_topic = row.get("quiz_topic") or DEFAULT_QUIZ_TOPIC
        difficulty = row.get("difficulty") or DEFAULT_DIFFICULTY
        quiz_time = row.get("quiz_time") or DEFAULT_QUIZ_TIME

        user_profile = await get_user_language_profile(telegram_user_id)
        if not user_profile:
            logger.info(
                f"Skipping daily quiz; no language selected | user_id={telegram_user_id}"
            )
            continue

        try:
            quiz_text = await generate_quiz_text_for_user(
                telegram_user_id=telegram_user_id,
                quiz_topic=quiz_topic,
                difficulty=difficulty,
                preferred_language_instruction=user_profile["instruction"],
            )

            await context.bot.send_message(
                chat_id=telegram_user_id,
                text=quiz_text,
            )

            await save_quiz_history(
                telegram_user_id=telegram_user_id,
                quiz_topic=quiz_topic,
                difficulty=difficulty,
                quiz_text=quiz_text,
            )

            next_run_at = compute_next_run_at(quiz_time, from_dt_utc=now_utc)

            await save_quiz_setting(
                telegram_user_id=telegram_user_id,
                next_run_at=next_run_at,
            )

            logger.info(
                f"Daily quiz sent successfully | user_id={telegram_user_id}"
            )
        except Exception as exc:
            logger.exception(
                f"Daily quiz failed | user_id={telegram_user_id} | error={exc}"
            )


def register_quiz_scheduler(application: Application) -> None:
    if application.job_queue is None:
        logger.warning("JobQueue is not available. Daily quiz scheduler is disabled.")
        return

    application.job_queue.run_repeating(
        send_due_quizzes,
        interval=300,
        first=60,
        name="daily_quiz_checker",
)
