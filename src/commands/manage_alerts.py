from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from telegram.helpers import escape_markdown
from dotenv import load_dotenv
import os

from src.utils.db_helper import get_user_by_telegram_id, get_all_patients_by_telegram_id, toggle_alerts


load_dotenv()
web_url = os.getenv("WEB_URL")

async def manage_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /manage_alerts is issued."""
    user = get_user_by_telegram_id(update.effective_user.id)
    
    if not user:
        await update.message.reply_text(
            f"You have not linked your account yet. Please head to the <a href='{web_url}'>WanderGuard Website</a> to link your account.",
            parse_mode='HTML'
        )
        return
    
    patients = get_all_patients_by_telegram_id(update.effective_user.id)
    
    if not patients:
        await update.message.reply_text("You have no patients under your care.")
        return
    
    message = "🔔 *Patient Alerts Management* 🔔" + \
        escape_markdown("\n======\nClick on a patient to toggle their alerts.\n🔔 Enabled\n🔕 Disabled", version=2)
    buttons = create_alert_buttons(patients)
        
        
    await update.message.reply_markdown_v2(message, reply_markup=InlineKeyboardMarkup(buttons))
    

async def handle_toggle_alerts(update: Update, context: CallbackContext) -> None:
    """Handle the callback button."""
    query = update.callback_query
    await query.edit_message_reply_markup(reply_markup=None)
    patient_uuid = query.data.split("_")[-1]
    toggle_alerts(patient_uuid)
    
    # update the message
    patients = get_all_patients_by_telegram_id(update.effective_user.id)
    
    buttons = create_alert_buttons(patients)
        
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


def create_alert_buttons(patients):
    buttons = []
    for patient in patients:    
        patient_name = patient.get('first_name') + " " + patient.get('last_name')
        emoji = "🔔" if patient.get('alerts') else "🔕"
        text = f"{emoji} {patient_name}\n"
        button = InlineKeyboardButton(text, callback_data=f"toggle_alerts_{patient.get('uuid')}")
        buttons.append([button])
    return buttons