from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from services.config import config
from services.logger import logger

from handlers.start import start
from handlers.help import help_command
from handlers.message import message_handler
from handlers.about import about_command
from handlers.language import language_command
from handlers.settings import settings_command


def create_application() -> Application:

    application = (
        Application.builder()
        .token(config.bot_token)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("settings", settings_command))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler,
        )
    )

    logger.info("Telegram application initialized successfully.")

    return application
