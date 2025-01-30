import time
from telegram import Update
from telegram.ext import ContextTypes
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('users')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    tele_user = update.effective_user
    
    welcome_message = (
        rf"Greetings {tele_user.mention_markdown()}! "
        "Welcome to WanderGuard AI telegram bot, im designed to help you monitor "
        "and receive real-time updates and alerts about your dementia patient(s). "
    )
    
    # check if args are passed
    if context.args != [] and len(context.args) == 1:
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
        
        # add telegram user to user record
        users_table.update_item(
            Key={'uuid': user['uuid']},
            UpdateExpression="set telegram_id = :tid",
            ExpressionAttributeValues={':tid': tele_user.id}
        )
            
        return await update.message.reply_markdown(f"Your WanderGuard account ({user['email']}) has been successfully linked!")

    await update.message.reply_markdown(welcome_message)
