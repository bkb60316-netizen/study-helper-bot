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
    logger.info(
        f"Saving chat history | user_id={telegram_user_id} | intent={intent}"
    )

    client = database.get_client()

    payload = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "first_name": first_name,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "intent": intent,
    }

    result = client.table("chat_history").insert(payload).execute()

    logger.info(
        f"Chat history insert response received | user_id={telegram_user_id}"
    )
    return result


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
        logger.info(
            f"Chat history saved successfully | user_id={telegram_user_id}"
        )
    except Exception as exc:
        logger.exception(
            f"Could not save chat history | user_id={telegram_user_id} | error={exc}"
)
