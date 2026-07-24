import asyncio

from services.database import database
from services.logger import logger


def _save_chat_history_sync(
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    user_message: str,
    bot_reply: str,
    intent: str,
) -> None:
    client = database.get_client()

    payload = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "first_name": first_name,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "intent": intent,
    }

    client.table("chat_history").insert(payload).execute()


async def save_chat_history(
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    user_message: str,
    bot_reply: str,
    intent: str,
) -> None:
    try:
        await asyncio.to_thread(
            _save_chat_history_sync,
            telegram_user_id,
            username,
            first_name,
            user_message,
            bot_reply,
            intent,
        )
    except Exception as exc:
        logger.warning(f"Could not save chat history: {exc}")
