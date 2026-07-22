from bot.app import create_application
from services.config import config
from services.logger import logger


def main():

    if not config.bot_token:
        raise ValueError(
            "BOT_TOKEN environment variable is missing."
        )

    logger.info("Starting Study Helper AI Bot...")

    application = create_application()

    logger.info("Bot started successfully.")

    application.run_polling()


if __name__ == "__main__":
    main()
