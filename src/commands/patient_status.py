from telegram import InlineKeyboardMarkup, Update, Bot, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from dotenv import load_dotenv
import os
import datetime

from src.utils.db_helper import get_all_patients_by_uuid, get_user_by_telegram_id, get_patient_status, user_patients
from src.utils.misc import time_difference_to_string, status_symbol

load_dotenv()
web_url = os.getenv("WEB_URL")

status_message_template = (
    "👤 <b>Patient Name:</b> {}\n"
    "⏱️ <b>Last Seen:</b> {}\n"
    "📏 <b>Distance from Safe Zone:</b> {}\n\n"
    "<b>🚶 Wandering Status:</b> {}\n"
    "❤️ <b>Heart Rate:</b> {} bpm\n"
    "🏃‍♂️ <b>Walking Speed:</b> {} m/s\n\n"
    "📍 <b>Last Seen Location:</b>"
)


async def patient_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /patient_status is issued."""
    user = get_user_by_telegram_id(update.effective_user.id)
    
    if not user:
        await update.message.reply_text(
            f"You have not linked your account yet. Please head to the <a href='{web_url}'>WanderGuard Website</a> to link your account.",
            parse_mode='HTML'
        )
        return
    
    patients = get_all_patients_by_uuid(user.get('uuid'))
    
    if not patients:
        await update.message.reply_text("You have no patients under your care.")
        return
    
    buttons = []
    for patient in patients:    
        patient_name = patient.get('first_name') + " " + patient.get('last_name')
        button = InlineKeyboardButton(patient_name, callback_data=patient.get('uuid'))
        buttons.append([button])
        
    await update.message.reply_text("Select a patient to view their status:", reply_markup=InlineKeyboardMarkup(buttons))
    

async def send_alert(bot: Bot, chat_id: str) -> None:
    message = "🚨 <b>ALERT</b> 🚨\n Your patient, John Doe, is wandering outside the safe zone. \n\n"
    message += status_message_template.format("John Doe", "a second ago", "15 meters", "Wandering 🔴", 106, 0.8)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    await bot.send_location(chat_id=chat_id, latitude=1.345382, longitude=103.9300886)
    

async def handle_button(update: Update, context: CallbackContext) -> None:
    """Handle the callback button."""
    query = update.callback_query
    await query.answer()
    
    patient_uuid = query.data
    telegram_id = query.from_user.id
    
    user = get_user_by_telegram_id(telegram_id)
    
    if not user:
        await query.message.reply_text(
            f"You have not linked your account yet. Please head to the <a href='{web_url}'>WanderGuard Website</a> to link your account.",
            parse_mode='HTML'
        )
        return
    
    patients = user_patients.get(user.get('uuid'))

    if not patients:
        # Fetch patient from database
        get_all_patients_by_uuid(user.get('uuid'))
    
    patient = user_patients.get(user.get('uuid')).get(patient_uuid)
    if not patient:
        await query.message.reply_text("Patient not found.")
        return
    
    patient_name = patient['first_name'] + ' ' + patient['last_name']

    patient_status = get_patient_status(patient_uuid)
    if not patient_status:
        await query.message.reply_text(f"No status data available for patient {patient_name}.")
        return
    
    # Extract patient status data
    status = patient_status.get('status')
    distance_from_safe_zone = patient_status.get('distance_from_safe_zone')
    timestamp = patient_status['timestamp']
    time_diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(float(timestamp))
    time_diff_string = time_difference_to_string(time_diff)
    status_str = status + " " + status_symbol(status)
    
    message = f"<b>{patient_name} Status</b>"
    message += status_message_template.format(
        patient_name,
        time_diff_string,
        int(distance_from_safe_zone) if int(distance_from_safe_zone) > 0 else "0",
        status_str,
        patient_status.get('heart_rate'),
        patient_status.get('speed')
    )
    
    # Send message
    await query.message.reply_text(message, parse_mode='HTML')
    await query.message.reply_location(latitude=1.345382, longitude=103.9300886)
