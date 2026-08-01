from services.ai_router import generate_response
from services.logger import logger


async def localize_ui_text(
    base_text: str,
    preferred_language_instruction: str | None,
) -> str:
    language = (preferred_language_instruction or "English").strip()

    if not language or language.lower() == "english":
        return base_text

    prompt = (
        f"Translate the following app UI text into {language}. "
        "Keep the meaning exactly the same. "
        "Preserve emojis, line breaks, command names like /start, /help, /language, /quiz, "
        "and any button labels. "
        "Do not add new information. "
        "Return only the translated text.\n\n"
        f"TEXT:\n{base_text}"
    )

    try:
        return await generate_response(
            user_text=prompt,
            intent="chat",
            history=[],
            preferred_language_instruction=language,
        )
    except Exception as exc:
        logger.warning(f"UI localization failed, using English fallback: {exc}")
        return base_text
