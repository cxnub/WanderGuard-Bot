"""
The WanderGuard AI telegram bot entry point.
"""
import logging
import os
from uuid import UUID
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from src.commands.start import start, unlink, unlink_email
from src.commands.help import help_command
from src.commands.patient_status import patient_status_command, handle_button

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Add this to your .env if you want a default recipient

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def start_bot() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("patient_status", patient_status_command))
    application.add_handler(CommandHandler("unlink", unlink))
    
    # Add CallbackQueryHandler for patient_status
    application.add_handler(CallbackQueryHandler(handle_button, pattern=is_uuid))
    
    # Add CallbackQueryHandler for unlink email
    application.add_handler(CallbackQueryHandler(unlink_email, pattern=r"^unlink_"))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def is_uuid(uuid: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid_obj = UUID(uuid, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid


if __name__ == "__main__":
    start_bot()
