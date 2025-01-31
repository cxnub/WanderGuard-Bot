import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.helpers import escape_markdown
import boto3
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

from src.utils.db_helper import unlink_telegram_id, get_user_by_telegram_id, get_user_by_email

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('users')

load_dotenv()
web_url = os.getenv("WEB_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    tele_user = update.effective_user
    
    welcome_message = (
        rf"Greetings {tele_user.mention_markdown_v2()}! "
        "Welcome to WanderGuard AI telegram bot, I'm designed to help you monitor "
        "and receive real-time updates and alerts about your dementia patient(s). "
    )
    
    # check if args are passed
    if not (context.args != [] and len(context.args) == 1):
        # check if user exists
        user = get_user_by_telegram_id(tele_user.id)
        if not user:
            welcome_message += f"\n\nTo get started, please link your WanderGuard account through the [WanderGuard Website]({web_url})."

        else:
            welcome_message += escape_markdown(f"\n\nYou may use the /help command to view all my commands.")

        return await update.message.reply_markdown(welcome_message)
        
    token = context.args[0]

    response = users_table.scan(
        FilterExpression=Attr('telegram_token').eq(token)
    )
    
    if len(response['Items']) == 0:
        return await update.message.reply_markdown("Invalid token. Please try again.")
    
    user = response['Items'][0]
        
    # check if token has expired
    if user['telegram_token_expiry'] < int(time.time()):
        return await update.message.reply_markdown("Token has expired. Please try again.")
    
    # check if telegram account is already linked
    existing_user = get_user_by_telegram_id(tele_user.id)
    
    if existing_user and existing_user['uuid'] != user['uuid']:
        return await update.message.reply_markdown(f"Your telegram account is already linked to another WanderGuard account ({existing_user['email']}). /unlink to unlink the current WanderGuard account.")
    
    if user.get('telegram_id'):
        if user['telegram_id'] == tele_user.id:
            return await update.message.reply_markdown(f"Your telegram account is already linked to your WanderGuard account ({user['email']}).")
        
        # get telegram user by telegram_id to get the mention
        unlink_button = InlineKeyboardButton("Unlink", callback_data=f"unlink_" + user['email'])
        return await update.message.reply_markdown(
            f"Your WanderGuard account ({user['email']}) is already linked to [this telegram account](tg://user?id={user['telegram_id']}).",
            reply_markup=InlineKeyboardMarkup([[unlink_button]])
            )
    
    
    # add telegram user to user record
    users_table.update_item(
        Key={'uuid': user['uuid']},
        UpdateExpression="set telegram_id = :tid",
        ExpressionAttributeValues={':tid': tele_user.id}
    )
        
    return await update.message.reply_markdown(f"Your WanderGuard account ({user['email']}) has been successfully linked!")



async def unlink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unlink telegram account from WanderGuard account."""
    tele_user = update.effective_user
    user = unlink_telegram_id(tele_user.id)
    if not user:
        return await update.message.reply_markdown("Your telegram account is not linked to any WanderGuard account.")
        
    await update.message.reply_markdown(
        f"Your telegram account has been successfully unlinked from your WanderGuard account ({user.get('email')}). You may link back anytime through the [WanderGuard Website]({web_url}).",
        )
    
async def unlink_email(update: Update, context: CallbackContext) -> None:
    """Unlink telegram account from WanderGuard account."""
    query = update.callback_query
    email = query.data.split('_')[1]
    
    user = get_user_by_email(email)
    if not user:
        return await query.message.reply_markdown("Your WanderGuard account is not linked to any telegram account.")
        
    await query.message.reply_markdown(
        f"[This telegram account](tg://user?id={user['telegram_id']}) has been successfully unlinked from your WanderGuard account ({user.get('email')}). You may link back anytime through the [WanderGuard Website]({web_url}).",
        )
    
    await query.answer()
    
    unlink_telegram_id(user['telegram_id'])
