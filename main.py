import logging
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder,ContextTypes,CommandHandler,MessageHandler,filters,CallbackQueryHandler
import os 
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi{user.mention_html()}! I'm your assistant. Send me an audio message, and I'll process it"

    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Van", callback_data='van')],
        [InlineKeyboardButton("School Close", callback_data='school_close')],   
        [InlineKeyboardButton("Fees", callback_data='fees')]
    ]
    reply = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please choose an option:", reply_markup=reply
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'van':
        await van(update, context)
    elif query.data == 'school_close':
        await school_close(update, context)
    elif query.data == 'fees':
        await fees(update, context)
    else:
        await query.edit_message_text(text="Unknown option selected.")

async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE):

    logger.info(f"Received text message;{update.message.text}")
    await update.message.reply_text(f"You said:{update.message.text}")

async def handle_other(update: Update,context:ContextTypes.DEFAULT_TYPE):
    logger.info("REcieved a non-text message (maybe audio?)")
    await update.message.reply_text(f"Thanks! I received a message, but I only handle text for now.")


async def van(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text("This is a van command")
    else:
        await update.message.reply_text("This is a van command")

async def school_close(update: Update,context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text("School is closed today, enjoy your day off!")
    else:
        await update.message.reply_text("School is closed today, enjoy your day off!")

async def fees(update: Update,context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.edit_message_text("The school fees are due on the 15th of every month. Please ensure you pay on time to avoid any penalties.")
    else:
        await update.message.reply_text("The school fees are due on the 15th of every month. Please ensure you pay on time to avoid any penalties.")

def main() -> None:

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("menu",menu))
    application.add_handler(MessageHandler(filters.TEXT & ~ filters.COMMAND,echo))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT,handle_other))
    application.add_handler(CommandHandler("van",van))
    application.add_handler(CommandHandler("school_close",school_close))
    application.add_handler(CommandHandler("fees",fees))
    
    application.add_handler(CallbackQueryHandler(button))

    print("Bot starting...")
    application.run_polling()
    print("Bot has stopped")

if __name__ == '__main__':
    main()
