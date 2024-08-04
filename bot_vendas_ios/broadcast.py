#broadcast.py
import logging
import asyncio
from telegram import Update, InputFile
from telegram.ext import ContextTypes, CommandHandler
from database import get_db_connection  # Usando o seu sistema de database existente
from config import ADMIN_ID  # Certifique-se de definir o ID do admin no seu config.py
import requests
import os

logger = logging.getLogger(__name__)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    message = update.message.reply_to_message
    if not message:
        await update.message.reply_text("Por favor, responda a uma mensagem para transmitir.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM users WHERE chat_id IS NOT NULL")
    users = cursor.fetchall()
    conn.close()

    if not users:
        logger.error("Nenhum usuário encontrado com chat_id válido.")
        await update.message.reply_text("Nenhum usuário encontrado para enviar a mensagem.")
        return

    os.makedirs('downloads', exist_ok=True)

    for user in users:
        chat_id = user['chat_id']
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
                file = await context.bot.get_file(file_id)
                file_path = file.file_path

                response = requests.get(file_path)
                image_path = os.path.join("downloads", f"{file_id}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(response.content)

                await context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'), caption=message.caption)
                os.remove(image_path)
            elif message.text:
                await context.bot.send_message(chat_id=chat_id, text=message.text)
            
            logger.info(f"Mensagem enviada para {chat_id}")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {chat_id}: {e}")

    await update.message.reply_text("Broadcast enviado com sucesso.")

def setup_broadcast_handlers(application):
    application.add_handler(CommandHandler("broadcast", broadcast))
