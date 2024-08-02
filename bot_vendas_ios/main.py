import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import API_KEY
from notifications import start_scheduled_jobs
from sales_simulation import simulate_sale_command
from resellers import create_reseller_command
from users import create_user_command
from menu import start_command, button_handler  # Importando o menu

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

def main():
    logger.info("Setting up application...")
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))  # Handler para botões inline
    application.add_handler(CommandHandler("createreseller", create_reseller_command))
    application.add_handler(CommandHandler("createuser", create_user_command))
    application.add_handler(CommandHandler("simulate_sale", simulate_sale_command))

    logger.info("Starting scheduled jobs...")
    start_scheduled_jobs()

    logger.info("Running the bot...")
    application.run_polling()

if __name__ == '__main__':
    logger.info("Bot is starting...")
    main()
