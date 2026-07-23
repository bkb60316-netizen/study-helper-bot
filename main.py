from bot.app import create_application
from services.config import config
from services.logger import logger

def main():
    if not config.bot_token:
        raise ValueError("BOT_TOKEN environment variable is missing.")
    if not config.webhook_url:
        raise ValueError("WEBHOOK_URL environment variable is missing.")

    logger.info("Starting Study Helper AI Bot...")
    application = create_application()
    logger.info("Bot started successfully in webhook mode.")

    application.run_webhook(
        listen="0.0.0.0",
        port=config.port,
        webhook_url=config.webhook_url,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
