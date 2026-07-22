import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Telegram
    bot_token: str = os.getenv("BOT_TOKEN", "")

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # AI Providers
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Default AI Provider
    default_ai_provider: str = os.getenv(
        "DEFAULT_AI_PROVIDER",
        "openrouter"
    )

    # App Settings
    bot_mode: str = os.getenv(
        "BOT_MODE",
        "production"
    )

    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


config = Config()
