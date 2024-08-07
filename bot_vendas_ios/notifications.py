#notifications.py
import requests
import logging
import schedule
import time
import threading
from config import API_KEY, TELEGRAM_CHAT_ID, ADMIN_ID
from users import get_active_users, get_inactive_users
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def notify_telegram(message, chat_id=TELEGRAM_CHAT_ID, pin_message=False):
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
        
        if pin_message:
            message_id = response.json().get("result", {}).get("message_id")
            if message_id:
                pin_url = f"https://api.telegram.org/bot{API_KEY}/pinChatMessage"
                pin_data = {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'disable_notification': True
                }
                pin_response = requests.post(pin_url, data=pin_data)
                pin_response.raise_for_status()
                logger.info(f"Message pinned to Telegram: {message_id}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Telegram: {e}")

async def send_message_in_chunks(text, chat_id, context, chunk_size=4096):
    # Divide o texto em pedaços menores se necessário
    for i in range(0, len(text), chunk_size):
        await context.bot.send_message(chat_id=chat_id, text=text[i:i+chunk_size], parse_mode="Markdown")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    logger.info("Received /report command")
    active_users = get_active_users()
    inactive_users = get_inactive_users()

    active_list = "\n".join([
        f"Usuário: `{user['username']}`\nVendido em: `{user['sale_date']}`\nValidade: `{user['validity_date']}`\n"
        for user in active_users
    ])

    inactive_list = "\n".join([
        f"Usuário: `{user['username']}`\nCriado em: `{user['creation_date']}`\nValidade: `{user['validity_date']}`\n"
        for user in inactive_users
    ])

    report_message = (
        f"📊 *Relatório Diário de Usuários* 📊\n\n"
        f"🟢 *Usuários Vendidos (Ativados):*\n{active_list or 'Nenhum usuário vendido ainda.'}\n\n"
        f"🔴 *Usuários Não Vendidos (Inativos):*\n{inactive_list or 'Nenhum usuário não vendido disponível.'}"
    )

    logger.info("Sending report to Telegram")
    await send_message_in_chunks(report_message, TELEGRAM_CHAT_ID, context)
    await update.message.reply_text("Relatório diário enviado ao canal.")

def send_daily_report():
    logger.info("Starting to generate daily report...")
    
    active_users = get_active_users()
    inactive_users = get_inactive_users()

    active_list = "\n".join([
        f"Usuário: `{user['username']}`\nVendido em: `{user['sale_date'] or 'N/A'}`\nValidade: `{user['validity_date']}`\n"
        for user in active_users
    ])

    inactive_list = "\n".join([
        f"Usuário: `{user['username']}`\nCriado em: `{user['creation_date']}`\nValidade: `{user['validity_date']}`\n"
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

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
