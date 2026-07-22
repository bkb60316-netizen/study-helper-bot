from telegram import Update
from telegram.ext import ContextTypes

from services.logger import logger


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user_message = update.message.text.strip()

    logger.info(
        f"Message Received: {user_message}"
    )

    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "good morning",
        "good evening",
        "good night",
    ]

    if user_message.lower() in greetings:

        await update.message.reply_text(
            "👋 Hello!\n\n"
            "मैं Study Helper AI हूँ।\n"
            "आप अपना कोई भी Study Question पूछ सकते हैं।"
        )

        return

    await update.message.reply_text(
        "🤖 AI System अभी तैयार किया जा रहा है।\n\n"
        "बहुत जल्द मैं आपके सभी सवालों का जवाब दूँगा।"
      )
