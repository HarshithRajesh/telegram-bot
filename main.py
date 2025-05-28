import logging
from telegram import Update
from telegram.ext import ApplicationBuilder,ContextTypes,CommandHandler,MessageHandler,filters
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

async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE):

    logger.info(f"REcieved text message;{update.message.text}")
    await update.message.reply_text(f"You said:{update.message.text}")

async def handle_other(update: Update,context:ContextTypes.DEFAULT_TYPE):
    logger.info("REcieved a non-text message (maybe audio?)")
    await update.message.reply_text(f"Thanks! I received a message, but I only handle text for now.")

def main() -> None:

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(MessageHandler(filters.TEXT & ~ filters.COMMAND,echo))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT,handle_other))

    print("Bot starting...")
    application.run_polling()
    print("Bot has stopped")

if __name__ == '__main__':
    main()
