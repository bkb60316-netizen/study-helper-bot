import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    webhook_url: str = os.getenv("WEBHOOK_URL", "")
    port: int = int(os.getenv("PORT", "10000"))
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    default_ai_provider: str = os.getenv("DEFAULT_AI_PROVIDER", "openrouter")
    bot_mode: str = os.getenv("BOT_MODE", "production")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()
