from bot.app import create_application
from services.logger import logger


def main():

    logger.info("Starting Study Helper AI Bot...")

    application = create_application()

    logger.info("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
