import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler
from database import get_db_connection
from config import BOT_NAME, DEFAULT_VALIDITY_DAYS, SUPPORT_CONTACT

logger = logging.getLogger(__name__)

def create_affiliate_link(user_id):
    return f"https://t.me/{BOT_NAME.lstrip('@')}?start={user_id}"

def record_affiliate_purchase(affiliate_id, referred_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    logger.info(f"Registrando compra para o afiliado {affiliate_id} referindo o usuário {referred_user_id}")
    
    cursor.execute('''
    INSERT INTO affiliates (affiliate_id, referred_user_id, timestamp)
    VALUES (?, ?, ?)
    ''', (affiliate_id, referred_user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()

    # Concede automaticamente um vale usuário de 30 dias ao afiliado
    success = grant_user_voucher(affiliate_id)
    
    conn.close()
    
    if success:
        logger.info(f"Vale usuário de 30 dias concedido ao afiliado {affiliate_id}")
    else:
        logger.error(f"Falha ao conceder vale usuário ao afiliado {affiliate_id}")

def get_affiliate_stats(affiliate_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT COUNT(*) as total_referred, MAX(timestamp) as last_referred_time, MAX(referred_user_id) as last_referred_user
    FROM affiliates WHERE affiliate_id = ?
    ''', (affiliate_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_referred': stats['total_referred'],
        'last_referred_user': stats['last_referred_user'] or 'n/a',
        'last_referred_time': stats['last_referred_time'] or 'Nenhuma ainda'
    }

async def affiliate_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = create_affiliate_link(user_id)
    stats = get_affiliate_stats(user_id)
    
    message = (
        f"*Receba um usuário de 30 dias sobre qualquer compra de seu afiliado:*\n\n"
        f"✅ *Total de indicados:* `{stats['total_referred']}`\n"
        f"🔎 *Último indicado:* `{stats['last_referred_user']}`\n"
        f"⌛ *Horário:* `{stats['last_referred_time']}`\n\n"
        f"🔗 *Seu Link:* `{link}`"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='back_to_start')]
    ]
    
    if update.message:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)

def setup_affiliate_handlers(application):
    application.add_handler(CommandHandler("affiliate_dashboard", affiliate_dashboard))

async def handle_affiliate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referrer_id = context.args[0] if context.args else None

    if referrer_id:
        logger.info(f"Usuário {user_id} iniciou o bot através do link de afiliação de {referrer_id}")
        context.user_data['referrer_id'] = referrer_id  # Armazena o ID do afiliado
        message = f"Você foi indicado por {referrer_id}."
        await update.message.reply_text(message)

def grant_user_voucher(affiliate_id):
    voucher_message = (
        "🎉 *Parabéns!* 🎉\n\n"
        "Você recebeu um *Vale Usuário* de 30 dias pelo sucesso em indicar um novo cliente! 🏆\n\n"
        f"Para resgatar seu usuário, por favor entre em contato com nosso suporte.\n\n"
        f"📞 *Suporte:* {SUPPORT_CONTACT}\n\n"
        "🕒 *Validade do Vale:* 30 dias a partir da data de recebimento.\n\n"
        "⚠️ *Instruções:*\n"
        "1. Envie esta mensagem ao nosso suporte.\n"
        "2. Aguarde o atendimento para receber seu usuário.\n\n"
        "Obrigado por confiar em nossos serviços! 🙌"
    )
    
    logger.info(f"Enviando vale usuário para o afiliado {affiliate_id}")
    return notify_affiliate(affiliate_id, voucher_message)

def notify_affiliate(affiliate_id, message):
    try:
        # Envia a mensagem ao afiliado
        context.bot.send_message(chat_id=affiliate_id, text=message, parse_mode=ParseMode.MARKDOWN)
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem ao afiliado {affiliate_id}: {e}")
        return False
