from telegram import ReplyKeyboardMarkup, Update, Bot
from telegram.ext import ContextTypes

from utils.db_helper import get_all_patients_by_telegram_id

status_message_template = (
    "<b>🩺 Patient Status</b>\n\n"
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
    # get all patients under the caregiver
    patients = get_all_patients_by_telegram_id(update.effective_user.id)
    
    if not patients:
        await update.message.reply_text("You have no patients under your care.")
        return
    
    # list all patients by name as buttons
    buttons = []
    for patient in patients:
        patient_name = patient.get('first_name') + " " + patient.get('last_name')
        buttons.append([patient_name, patient.get('uuid')])
        
    await update.message.reply_text("Select a patient to view their status:", reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True))
    

async def send_alert(bot: Bot, chat_id: str) -> None:
    message = "🚨 <b>ALERT</b> 🚨\n Your patient, John Doe, is wandering outside the safe zone. \n\n"
    message += status_message_template.format("John Doe", "a second ago", "15 meters", "Wandering 🔴", 106, 0.8)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    await bot.send_location(chat_id=chat_id, latitude=1.345382, longitude=103.9300886)