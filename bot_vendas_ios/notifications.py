import requests
import logging
import schedule
import time
import threading
from config import API_KEY, TELEGRAM_CHAT_ID
from users import get_active_users, get_inactive_users
from telegram import Update  # Importando Update
from telegram.ext import ContextTypes  # Importando ContextTypes

logger = logging.getLogger(__name__)

def notify_telegram(message, chat_id=TELEGRAM_CHAT_ID):
    url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': "Markdown",
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info(f"Message sent to Telegram: {message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Telegram: {e}")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /report command")
    active_users = get_active_users()
    inactive_users = get_inactive_users()

    active_list = "\n".join([
        f"Usuário: `{user['username']}` - Vendido em: {user['sale_date']} - Validade: {user['validity_date']}"
        for user in active_users
    ])

    inactive_list = "\n".join([
        f"Usuário: `{user['username']}` - Criado em: {user['validity_date']} - Validade: {user['validity_date']}"
        for user in inactive_users
    ])

    report_message = (
        f"📊 *Relatório Diário de Usuários* 📊\n\n"
        f"🟢 *Usuários Vendidos (Ativados):*\n{active_list or 'Nenhum usuário vendido ainda.'}\n\n"
        f"🔴 *Usuários Não Vendidos (Inativos):*\n{inactive_list or 'Nenhum usuário não vendido disponível.'}"
    )

    logger.info("Sending report to Telegram")
    notify_telegram(report_message, chat_id=TELEGRAM_CHAT_ID)
    await update.message.reply_text("Relatório diário enviado ao canal.")

def send_daily_report():
    # Esta função pode ser chamada diariamente por um agendamento
    logger.info("Starting to generate daily report...")
    # Reutiliza a lógica de report_command para enviar o relatório diário
    active_users = get_active_users()
    inactive_users = get_inactive_users()

    active_list = "\n".join([
        f"Usuário: `{user['username']}` - Vendido em: {user['sale_date']} - Validade: {user['validity_date']}"
        for user in active_users
    ])

    inactive_list = "\n".join([
        f"Usuário: `{user['username']}` - Criado em: {user['validity_date']} - Validade: {user['validity_date']}"
        for user in inactive_users
    ])

    report_message = (
        f"📊 *Relatório Diário de Usuários* 📊\n\n"
        f"🟢 *Usuários Vendidos (Ativados):*\n{active_list or 'Nenhum usuário vendido ainda.'}\n\n"
        f"🔴 *Usuários Não Vendidos (Inativos):*\n{inactive_list or 'Nenhum usuário não vendido disponível.'}"
    )

    notify_telegram(report_message, chat_id=TELEGRAM_CHAT_ID)
    logger.info("Daily report sent.")

# Agendar o relatório para ser enviado todos os dias às 08:00 AM
schedule.every().day.at("08:00").do(send_daily_report)
logger.info("Scheduled daily report at 08:00 AM.")

def start_scheduled_jobs():
    logger.info("Starting scheduled jobs...")

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)  # Evitar uso excessivo de CPU

    # Rodar o agendamento em uma nova thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
