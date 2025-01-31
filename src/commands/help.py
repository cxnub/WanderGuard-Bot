from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_message = """
    Here are the commands you can use:
    /start - Start the bot
    /help - Show this help message
    /patient_status - View the status of your patients
    /unlink - Unlink your WanderGuard account
    /manage_alerts - Manage alerts for your patients
    """
    await update.message.reply_text(help_message)
