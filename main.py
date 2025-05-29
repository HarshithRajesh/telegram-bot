import logging
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder,ContextTypes,CommandHandler,MessageHandler,filters,CallbackQueryHandler
import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
import calendar

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

dynamic_messages = {
    'van': [
        "ವ್ಯಾನ್ ಸಮಯಕ್ಕೆ ಬರುತ್ತದೆ",
        "ವ್ಯಾನ್ ತಡವಾಗಿ ಬರಲಿದೆ. ದಯವಿಟ್ಟು ಕಾಯಿರಿ",
        "ವ್ಯಾನ್ ಇಂದು ಬರುವುದಿಲ್ಲ",
        "ವ್ಯಾನ್ ಮೈಂಟೆನೆನ್ಸ್ ನಲ್ಲಿದೆ"
    ],
    'school': [
        "ಶಾಲೆ ತೆರೆದಿದೆ",
        "ಶಾಲೆ ಮುಚ್ಚಿದೆ - ರಜೆ",
        "ಶಾಲೆ ಮುಚ್ಚಿದೆ - ವಿಶೇಷ ಕಾರ್ಯಕ್ರಮ",
        "ಶಾಲೆ ಅರ್ಧ ದಿನ"
    ],
    'fees': [
        "ಶಾಲಾ ಶುಲ್ಕ ಪಾವತಿಸಿದೆ",
        "ಶಾಲಾ ಶುಲ್ಕ ಬಾಕಿ ಇದೆ",
        "ಶಾಲಾ ಶುಲ್ಕ ದಿನಾಂಕ ವಿಸ್ತರಿಸಲಾಗಿದೆ",
        "ಹೊಸ ಶುಲ್ಕ ರಚನೆ ಪ್ರಕಟಿಸಲಾಗಿದೆ"
    ]
}

scheduled_messages = {
    'van': {},
    'school': {},
    'fees': {}
}

user_states = {}

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your assistant. Use /menu to see available options."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚐 ವ್ಯಾನ್", callback_data='van')],
        [InlineKeyboardButton("🏫 ಶಾಲೆ", callback_data='school_close')],
        [InlineKeyboardButton("💰 ಶಾಲಾ ಶುಲ್ಕ", callback_data='fees')]
    ]
    reply = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "ದಯವಿಟ್ಟು ಒಂದು ಆಯ್ಕೆಯನ್ನು ಆರಿಸಿ:", reply_markup=reply
        )
    else:
        await update.message.reply_text(
            "ದಯವಿಟ್ಟು ಒಂದು ಆಯ್ಕೆಯನ್ನು ಆರಿಸಿ:", reply_markup=reply
        )

async def van_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏰ ವ್ಯಾನ್ ಸಮಯಕ್ಕೆ ಬರುತ್ತದೆ", callback_data='van_ontime')],
        [InlineKeyboardButton("⏳ ವ್ಯಾನ್ ತಡವಾಗಿ ಬರುತ್ತದೆ", callback_data='van_late')],
        [InlineKeyboardButton("❌ ವ್ಯಾನ್ ಬರುವುದಿಲ್ಲ", callback_data='van_not_coming')],
        [InlineKeyboardButton("🔧 ವ್ಯಾನ್ ಮೈಂಟೆನೆನ್ಸ್", callback_data='van_maintenance')],
        [InlineKeyboardButton("📋 ವೇಳಾಪಟ್ಟಿ ನೋಡಿ", callback_data='van_view_schedule')],
        [InlineKeyboardButton("🔙 ಮುಖ್ಯ ಮೆನು", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("🚐 ವ್ಯಾನ್ ಆಯ್ಕೆಗಳು:", reply_markup=reply_markup)

async def school_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ ಶಾಲೆ ತೆರೆದಿದೆ", callback_data='school_open')],
        [InlineKeyboardButton("🏖️ ಶಾಲೆ ಮುಚ್ಚಿದೆ - ರಜೆ", callback_data='school_holiday')],
        [InlineKeyboardButton("🎉 ಶಾಲೆ ಮುಚ್ಚಿದೆ - ಕಾರ್ಯಕ್ರಮ", callback_data='school_event')],
        [InlineKeyboardButton("⏰ ಶಾಲೆ ಅರ್ಧ ದಿನ", callback_data='school_halfday')],
        [InlineKeyboardButton("📋 ವೇಳಾಪಟ್ಟಿ ನೋಡಿ", callback_data='school_view_schedule')],
        [InlineKeyboardButton("🔙 ಮುಖ್ಯ ಮೆನು", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("🏫 ಶಾಲೆ ಆಯ್ಕೆಗಳು:", reply_markup=reply_markup)

async def fees_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ ಶುಲ್ಕ ಪಾವತಿಸಿದೆ", callback_data='fees_paid')],
        [InlineKeyboardButton("💸 ಶುಲ್ಕ ಬಾಕಿ ಇದೆ", callback_data='fees_pending')],
        [InlineKeyboardButton("📅 ಶುಲ್ಕ ದಿನಾಂಕ ವಿಸ್ತರಿಸಿದೆ", callback_data='fees_extended')],
        [InlineKeyboardButton("📢 ಹೊಸ ಶುಲ್ಕ ರಚನೆ", callback_data='fees_new_structure')],
        [InlineKeyboardButton("📋 ವೇಳಾಪಟ್ಟಿ ನೋಡಿ", callback_data='fees_view_schedule')],
        [InlineKeyboardButton("🔙 ಮುಖ್ಯ ಮೆನು", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("💰 ಶುಲ್ಕ ಆಯ್ಕೆಗಳು:", reply_markup=reply_markup)

def create_calendar(year, month, category, message_type):
    """Create a calendar keyboard for date selection"""
    keyboard = []
    
    # Header with month/year
    month_name = calendar.month_name[month]
    keyboard.append([InlineKeyboardButton(f"📅 {month_name} {year}", callback_data='ignore')])
    
    # Navigation buttons
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    keyboard.append([
        InlineKeyboardButton("⬅️", callback_data=f'cal_prev_{prev_year}_{prev_month}_{category}_{message_type}'),
        InlineKeyboardButton("📅 ಇಂದು", callback_data=f'cal_today_{category}_{message_type}'),
        InlineKeyboardButton("➡️", callback_data=f'cal_next_{next_year}_{next_month}_{category}_{message_type}')
    ])
    
    # Day headers
    keyboard.append([
        InlineKeyboardButton("ಸೋ", callback_data='ignore'),
        InlineKeyboardButton("ಮಂ", callback_data='ignore'),
        InlineKeyboardButton("ಬು", callback_data='ignore'),
        InlineKeyboardButton("ಗು", callback_data='ignore'),
        InlineKeyboardButton("ಶು", callback_data='ignore'),
        InlineKeyboardButton("ಶ", callback_data='ignore'),
        InlineKeyboardButton("ಭ", callback_data='ignore')
    ])
    
    # Calendar days
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data='ignore'))
            else:
                callback_data = f'cal_select_{year}_{month:02d}_{day:02d}_{category}_{message_type}'
                row.append(InlineKeyboardButton(str(day), callback_data=callback_data))
        keyboard.append(row)
    
    # Back button
    keyboard.append([InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data=f'{category}_menu')])
    
    return InlineKeyboardMarkup(keyboard)

async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, category, message_type, year=None, month=None):
    """Show calendar for date selection"""
    if year is None or month is None:
        now = datetime.now()
        year, month = now.year, now.month
    
    # Store user state
    user_id = update.effective_user.id
    user_states[user_id] = {
        'category': category,
        'message_type': message_type,
        'step': 'selecting_date'
    }
    
    keyboard = create_calendar(year, month, category, message_type)
    await update.callback_query.edit_message_text(
        f"📅 {message_type} ಗಾಗಿ ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ:", 
        reply_markup=keyboard
    )

async def view_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE, category):
    if not scheduled_messages[category]:
        keyboard = [[InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data=f'{category}_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            f"📋 {category.upper()} ಗಾಗಿ ಯಾವುದೇ ವೇಳಾಪಟ್ಟಿ ಇಲ್ಲ.",
            reply_markup=reply_markup
        )
        return
    
    schedule_text = f"📋 {category.upper()} ವೇಳಾಪಟ್ಟಿ:\n\n"
    for date, message in scheduled_messages[category].items():
        schedule_text += f"📅 {date}: {message}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🗑️ ವೇಳಾಪಟ್ಟಿ ಅಳಿಸಿ", callback_data=f'{category}_clear_schedule')],
        [InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data=f'{category}_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(schedule_text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    print(f"Received callback_data: '{query.data}'")
    logger.info(f"Callback data: {query.data}")
    
    # Ignore empty callbacks
    if query.data == 'ignore':
        return
    
    # Main menu navigation
    if query.data == 'van':
        await van_menu(update, context)
    elif query.data == 'school_close':
        await school_menu(update, context)
    elif query.data == 'fees':
        await fees_menu(update, context)
    elif query.data == 'back_to_menu':
        await menu(update, context)
    elif query.data == 'van_menu':
        await van_menu(update, context)
    elif query.data == 'school_menu':
        await school_menu(update, context)
    elif query.data == 'fees_menu':
        await fees_menu(update, context)
    
    # Van submenu options - show calendar
    elif query.data == 'van_ontime':
        await show_calendar(update, context, 'van', 'ವ್ಯಾನ್ ಸಮಯಕ್ಕೆ ಬರುತ್ತದೆ')
    elif query.data == 'van_late':
        await show_calendar(update, context, 'van', 'ವ್ಯಾನ್ ತಡವಾಗಿ ಬರುತ್ತದೆ')
    elif query.data == 'van_not_coming':
        await show_calendar(update, context, 'van', 'ವ್ಯಾನ್ ಬರುವುದಿಲ್ಲ')
    elif query.data == 'van_maintenance':
        await show_calendar(update, context, 'van', 'ವ್ಯಾನ್ ಮೈಂಟೆನೆನ್ಸ್')
    elif query.data == 'van_view_schedule':
        await view_schedule(update, context, 'van')
    elif query.data == 'van_clear_schedule':
        scheduled_messages['van'].clear()
        keyboard = [[InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data='van_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🗑️ ವ್ಯಾನ್ ವೇಳಾಪಟ್ಟಿ ಅಳಿಸಲಾಗಿದೆ", reply_markup=reply_markup)
    
    # School submenu options - show calendar
    elif query.data == 'school_open':
        await show_calendar(update, context, 'school', 'ಶಾಲೆ ತೆರೆದಿದೆ')
    elif query.data == 'school_holiday':
        await show_calendar(update, context, 'school', 'ಶಾಲೆ ಮುಚ್ಚಿದೆ - ರಜೆ')
    elif query.data == 'school_event':
        await show_calendar(update, context, 'school', 'ಶಾಲೆ ಮುಚ್ಚಿದೆ - ಕಾರ್ಯಕ್ರಮ')
    elif query.data == 'school_halfday':
        await show_calendar(update, context, 'school', 'ಶಾಲೆ ಅರ್ಧ ದಿನ')
    elif query.data == 'school_view_schedule':
        await view_schedule(update, context, 'school')
    elif query.data == 'school_clear_schedule':
        scheduled_messages['school'].clear()
        keyboard = [[InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data='school_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🗑️ ಶಾಲೆ ವೇಳಾಪಟ್ಟಿ ಅಳಿಸಲಾಗಿದೆ", reply_markup=reply_markup)
    
    # Fees submenu options - show calendar
    elif query.data == 'fees_paid':
        await show_calendar(update, context, 'fees', 'ಶುಲ್ಕ ಪಾವತಿಸಿದೆ')
    elif query.data == 'fees_pending':
        await show_calendar(update, context, 'fees', 'ಶುಲ್ಕ ಬಾಕಿ ಇದೆ')
    elif query.data == 'fees_extended':
        await show_calendar(update, context, 'fees', 'ಶುಲ್ಕ ದಿನಾಂಕ ವಿಸ್ತರಿಸಲಾಗಿದೆ')
    elif query.data == 'fees_new_structure':
        await show_calendar(update, context, 'fees', 'ಹೊಸ ಶುಲ್ಕ ರಚನೆ')
    elif query.data == 'fees_view_schedule':
        await view_schedule(update, context, 'fees')
    elif query.data == 'fees_clear_schedule':
        scheduled_messages['fees'].clear()
        keyboard = [[InlineKeyboardButton("🔙 ಹಿಂದೆ", callback_data='fees_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🗑️ ಶುಲ್ಕ ವೇಳಾಪಟ್ಟಿ ಅಳಿಸಲಾಗಿದೆ", reply_markup=reply_markup)
    
    # Calendar navigation
    elif query.data.startswith('cal_'):
        await handle_calendar_callback(update, context)
    
    else:
        await query.edit_message_text(text="ಅಜ್ಞಾತ ಆಯ್ಕೆ ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ.")

async def handle_calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_parts = query.data.split('_')
    
    if data_parts[1] == 'prev':
        # Previous month
        year, month, category, message_type = int(data_parts[2]), int(data_parts[3]), data_parts[4], '_'.join(data_parts[5:])
        await show_calendar(update, context, category, message_type, year, month)
    
    elif data_parts[1] == 'next':
        # Next month
        year, month, category, message_type = int(data_parts[2]), int(data_parts[3]), data_parts[4], '_'.join(data_parts[5:])
        await show_calendar(update, context, category, message_type, year, month)
    
    elif data_parts[1] == 'today':
        # Today
        today = datetime.now()
        category, message_type = data_parts[2], '_'.join(data_parts[3:])
        selected_date = today.strftime('%d/%m/%Y')
        await save_scheduled_message(update, context, category, message_type, selected_date)
    
    elif data_parts[1] == 'select':
        # Date selected
        year, month, day = int(data_parts[2]), int(data_parts[3]), int(data_parts[4])
        category, message_type = data_parts[5], '_'.join(data_parts[6:])
        selected_date = f"{day:02d}/{month:02d}/{year}"
        await save_scheduled_message(update, context, category, message_type, selected_date)

async def save_scheduled_message(update: Update, context: ContextTypes.DEFAULT_TYPE, category, message_type, selected_date):
    # Save to scheduled messages
    scheduled_messages[category][selected_date] = message_type
    
    # Clear user state
    user_id = update.effective_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    keyboard = [
        [InlineKeyboardButton("📋 ವೇಳಾಪಟ್ಟಿ ನೋಡಿ", callback_data=f'{category}_view_schedule')],
        [InlineKeyboardButton("🔙 ಮುಖ್ಯ ಮೆನು", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"✅ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ!\n\n"
        f"📅 ದಿನಾಂಕ: {selected_date}\n"
        f"📂 ವರ್ಗ: {category.upper()}\n"
        f"💬 ಸಂದೇಶ: {message_type}",
        reply_markup=reply_markup
    )

async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received text message: {update.message.text}")
    await update.message.reply_text(f"You said: {update.message.text}\n\nUse /menu to see available options.")

async def handle_other(update: Update,context:ContextTypes.DEFAULT_TYPE):
    logger.info("Received a non-text message (maybe audio?)")
    await update.message.reply_text("Thanks! I received a message, but I only handle text for now.\n\nUse /menu to see available options.")

# Legacy functions for backward compatibility
async def van(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await van_menu(update, context)

async def school_close(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await school_menu(update, context)

async def fees(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await fees_menu(update, context)

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("menu",menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("van",van))
    application.add_handler(CommandHandler("school_close",school_close))
    application.add_handler(CommandHandler("fees",fees))
    application.add_handler(MessageHandler(filters.TEXT & ~ filters.COMMAND,echo))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT,handle_other))

    print("Bot starting...")
    application.run_polling()
    print("Bot has stopped")

if __name__ == '__main__':
    main()
