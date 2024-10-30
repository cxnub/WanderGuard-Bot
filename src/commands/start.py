from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    welcome_message = (
        rf"Greetings {user.mention_markdown()}! "
        "Welcome to WanderGuard AI telegram bot, im designed to help you monitor "
        "and receive real-time updates and alerts about your dementia patient(s). "
    )

    await update.message.reply_markdown(welcome_message)
