import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import API_KEY
from notifications import start_scheduled_jobs, report_command
from sales_simulation import simulate_sale_command
from resellers import create_reseller_command
from users import create_user_command
from menu import start_command, button_handler, revenda_menu
from affiliate_system import setup_affiliate_handlers, handle_affiliate_start
from broadcast import setup_broadcast_handlers
from database import get_db_connection  # Adicionado para registrar os usuários

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Registra o usuário na tabela 'users'
    chat_id = update.effective_user.id
    username = update.effective_user.username

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO users (chat_id, username)
    VALUES (?, ?)
    ''', (chat_id, username))

    conn.commit()
    conn.close()
    logger.info(f"Usuário {chat_id} ({username}) registrado no banco de dados.")

    # Verifica se o usuário iniciou o bot com um link de afiliado
    if context.args:
        await handle_affiliate_start(update, context)
    await start_command(update, context)

def main():
    logger.info("Setting up application...")
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))  # Handler para botões inline
    application.add_handler(CommandHandler("createreseller", create_reseller_command))
    application.add_handler(CommandHandler("createuser", create_user_command))
    application.add_handler(CommandHandler("simulate_sale", simulate_sale_command))
    application.add_handler(CommandHandler("report", report_command))  # Adicionando handler para /report

    # Adicionando handler para o sub-menu de revenda
    application.add_handler(CallbackQueryHandler(revenda_menu, pattern='revenda_menu'))
    application.add_handler(CallbackQueryHandler(start_command, pattern='start'))  # Voltar ao início

    # Configurando o sistema de afiliação
    setup_affiliate_handlers(application)

    # Configurando o sistema de broadcast
    setup_broadcast_handlers(application)

    logger.info("Starting scheduled jobs...")
    start_scheduled_jobs()

    logger.info("Running the bot...")
    application.run_polling()

if __name__ == '__main__':
    logger.info("Bot is starting...")
    main()
