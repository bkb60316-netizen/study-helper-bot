from services.database import database
from services.logger import logger


def get_recent_chat_history(
    telegram_user_id: int,
    limit: int = 6,
) -> list[dict]:
    """
    Fetch recent chat history for a user from Supabase.
    Returns messages in chronological order.
    """
    try:
        client = database.get_client()

        response = (
            client.table("chat_history")
            .select("user_message, bot_reply, intent, created_at")
            .eq("telegram_user_id", telegram_user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        rows = response.data or []
        rows.reverse()

        history: list[dict] = []

        for row in rows:
            user_message = row.get("user_message")
            bot_reply = row.get("bot_reply")

            if user_message:
                history.append(
                    {
                        "role": "user",
                        "content": user_message,
                    }
                )

            if bot_reply:
                history.append(
                    {
                        "role": "assistant",
                        "content": bot_reply,
                    }
                )

        return history

    except Exception as exc:
        logger.warning(f"Could not fetch chat memory: {exc}")
        return []
