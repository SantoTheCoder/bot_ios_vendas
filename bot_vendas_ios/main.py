import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import API_KEY
from notifications import notify_telegram, start_scheduled_jobs, report_command
from sales_simulation import simulate_sale_command
from resellers import create_reseller_command
from users import create_user_command

# Corrigir a formatação do logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Corrigido para levelname
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /start command")
    await update.message.reply_text('Bem-vindo ao Bot de Vendas para iOS!')

def main():
    logger.info("Setting up application...")
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("createreseller", create_reseller_command))
    application.add_handler(CommandHandler("createuser", create_user_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("simulate_sale", simulate_sale_command))

    logger.info("Starting scheduled jobs...")
    start_scheduled_jobs()

    logger.info("Running the bot...")
    application.run_polling()

if __name__ == '__main__':
    logger.info("Bot is starting...")
    main()
