import httpx

from services.config import config
from services.logger import logger
from services.prompts import build_system_prompt


class AIRouterError(Exception):
    pass


async def generate_response(user_text: str, intent: str = "chat") -> str:
    provider = (config.default_ai_provider or "openrouter").lower().strip()

    providers = []
    if provider == "google":
        providers = [_generate_with_google, _generate_with_openrouter]
    else:
        providers = [_generate_with_openrouter, _generate_with_google]

    last_error: Exception | None = None

    for handler in providers:
        try:
            return await handler(user_text=user_text, intent=intent)
        except Exception as exc:
            last_error = exc
            logger.warning(f"AI provider failed: {handler.__name__} | {exc}")

    logger.exception("All AI providers failed")
    raise AIRouterError("All AI providers failed") from last_error


async def _generate_with_openrouter(user_text: str, intent: str) -> str:
    if not config.openrouter_api_key:
        raise AIRouterError("OPENROUTER_API_KEY is missing")

    system_prompt = build_system_prompt(intent)

    payload = {
        "model": config.openrouter_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"Bearer {config.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/bkb60316-netizen/study-helper-bot",
        "X-Title": "Study Helper AI",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
        if not content:
            raise AIRouterError("OpenRouter returned empty content")
        return content.strip()
    except (KeyError, IndexError) as exc:
        raise AIRouterError("Unexpected OpenRouter response format") from exc


async def _generate_with_google(user_text: str, intent: str) -> str:
    if not config.google_api_key:
        raise AIRouterError("GOOGLE_API_KEY is missing")

    system_prompt = build_system_prompt(intent)

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{config.google_model}:generateContent"
        f"?key={config.google_api_key}"
    )

    payload = {
        "systemInstruction": {
            "parts": [
                {"text": system_prompt}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise AIRouterError("Google AI returned no candidates")

        content = candidates[0]["content"]["parts"][0]["text"]
        if not content:
            raise AIRouterError("Google AI returned empty content")

        return content.strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise AIRouterError("Unexpected Google AI response format") from exc
