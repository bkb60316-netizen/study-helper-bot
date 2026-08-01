import asyncio
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.database import database
from services.logger import logger

LANGUAGE_PROFILES = {
    "en": {
        "display_name": "English",
        "native_name": "English",
        "instruction": "English",
    },
    "hi": {
        "display_name": "Hindi",
        "native_name": "हिंदी",
        "instruction": "Hindi in Devanagari script",
    },
    "bn": {
        "display_name": "Bengali",
        "native_name": "বাংলা",
        "instruction": "Bengali script",
    },
    "mr": {
        "display_name": "Marathi",
        "native_name": "मराठी",
        "instruction": "Marathi in Devanagari script",
    },
    "gu": {
        "display_name": "Gujarati",
        "native_name": "ગુજરાતી",
        "instruction": "Gujarati script",
    },
    "ta": {
        "display_name": "Tamil",
        "native_name": "தமிழ்",
        "instruction": "Tamil script",
    },
    "te": {
        "display_name": "Telugu",
        "native_name": "తెలుగు",
        "instruction": "Telugu script",
    },
    "kn": {
        "display_name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "instruction": "Kannada script",
    },
    "ml": {
        "display_name": "Malayalam",
        "native_name": "മലയാളം",
        "instruction": "Malayalam script",
    },
    "pa": {
        "display_name": "Punjabi",
        "native_name": "ਪੰਜਾਬੀ",
        "instruction": "Punjabi in Gurmukhi script",
    },
    "ur": {
        "display_name": "Urdu",
        "native_name": "اردو",
        "instruction": "Urdu in Arabic script",
    },
    "or": {
        "display_name": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "instruction": "Odia script",
    },
    "as": {
        "display_name": "Assamese",
        "native_name": "অসমীয়া",
        "instruction": "Assamese script",
    },
    "ne": {
        "display_name": "Nepali",
        "native_name": "नेपाली",
        "instruction": "Nepali in Devanagari script",
    },
}

LANGUAGE_ROWS = [
    ["en", "hi"],
    ["bn", "mr"],
    ["gu", "ta"],
    ["te", "kn"],
    ["ml", "pa"],
    ["ur", "or"],
    ["as", "ne"],
]


def get_language_profile(language_code: str | None) -> dict | None:
    if not language_code:
        return None

    code = language_code.strip().lower()
    profile = LANGUAGE_PROFILES.get(code)
    if profile is None:
        return None

    return {"code": code, **profile}


def get_language_instruction(language_code: str | None) -> str:
    profile = get_language_profile(language_code)
    if profile is None:
        return "English"
    return profile["instruction"]


def build_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = []

    for row_codes in LANGUAGE_ROWS:
        row = []
        for code in row_codes:
            profile = LANGUAGE_PROFILES[code]
            row.append(
                InlineKeyboardButton(
                    text=profile["native_name"],
                    callback_data=f"lang:{code}",
                )
            )
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def build_language_prompt_text(current_language_name: str | None = None) -> str:
    parts = []

    if current_language_name:
        parts.append(f"Current language: {current_language_name}")
        parts.append("")

    parts.extend(
        [
            "🌐 Choose the language you want to study in.",
            "",
            "After you select a language:",
            "• AI replies will be in that language",
            "• Daily quiz will follow that language",
            "• You can change it anytime with /language",
        ]
    )

    return "\n".join(parts)


def build_language_required_text() -> str:
    return (
        "🌐 Please choose your study language first.\n\n"
        "Use /language or tap a language below."
    )


def build_language_selected_text(language_code: str) -> str:
    profile = get_language_profile(language_code) or get_language_profile("en")
    return (
        f"✅ Language set to {profile['native_name']}.\n\n"
        f"From now on I will reply in {profile['display_name']}.\n"
        "You can change it anytime with /language."
    )


def _fetch_user_settings_sync(telegram_user_id: int) -> dict | None:
    client = database.get_client()

    response = (
        client.table("user_settings")
        .select("*")
        .eq("telegram_user_id", telegram_user_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []
    return rows[0] if rows else None


def _upsert_user_settings_sync(
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str,
    language_name: str,
) -> dict:
    client = database.get_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    existing = _fetch_user_settings_sync(telegram_user_id)

    payload = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "first_name": first_name,
        "language_code": language_code,
        "language_name": language_name,
        "updated_at": now_iso,
    }

    if existing:
        client.table("user_settings").update(payload).eq(
            "telegram_user_id", telegram_user_id
        ).execute()
    else:
        payload["created_at"] = now_iso
        client.table("user_settings").insert(payload).execute()

    return _fetch_user_settings_sync(telegram_user_id) or payload


async def get_user_settings(telegram_user_id: int) -> dict | None:
    return await asyncio.to_thread(_fetch_user_settings_sync, telegram_user_id)


async def get_user_language_code(telegram_user_id: int) -> str | None:
    settings = await get_user_settings(telegram_user_id)
    if not settings:
        return None
    return settings.get("language_code")


async def get_user_language_profile(telegram_user_id: int) -> dict | None:
    language_code = await get_user_language_code(telegram_user_id)
    return get_language_profile(language_code)


async def set_user_language(
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str,
) -> dict:
    profile = get_language_profile(language_code)
    if profile is None:
        raise ValueError("Unsupported language code.")

    return await asyncio.to_thread(
        _upsert_user_settings_sync,
        telegram_user_id,
        username,
        first_name,
        profile["code"],
        profile["display_name"],
    )


async def has_language_selected(telegram_user_id: int) -> bool:
    return (await get_user_language_code(telegram_user_id)) is not None
