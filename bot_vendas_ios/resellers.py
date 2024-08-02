#resellers.py
import logging
from config import IOS_API_KEY, DEFAULT_RESELLER_LIMIT
from notifications import notify_telegram
from utils import make_request, generate_random_string
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

logger = logging.getLogger(__name__)

def create_reseller(limit=DEFAULT_RESELLER_LIMIT, username=None, password=None):
    if username is None:
        username = generate_random_string(6)  # Gera nome de usuário com 6 caracteres
    if password is None:
        password = generate_random_string(6)  # Gera senha com 6 caracteres

    data = {
        'passapi': IOS_API_KEY,
        'module': 'createrev',
        'user': username,
        'pass': password,
        'admincid': 1,  # Ajuste conforme necessário
        'userlimite': limit,
        'whatsapp': "1234567890"
    }

    result = make_request(data)

    if 'error' not in result:
        success_message = (
            "🎉 *Revendedor Criado* 🎉\n\n"
            "🔎 *Usuário:*\n"
            f"`{username}`\n\n"
            "🔑 *Senha:*\n"
            f"`{password}`\n\n"
            "🎯 *Validade:*\n"
            "30 dias\n\n"
            "🕟 *Limite:*\n"
            f"{limit}\n\n"
            "💥 Obrigado por usar nossos serviços!\n\n"
            "🔗 [*Link do Painel (Clique Aqui)*](https://poisonbrasil.atlasssh.com/)\n\n"
            "Suporte: @Pedrooo"
        )
        notify_telegram(success_message)
        logger.info(success_message)

        # Adicionando informações financeiras na notificação ao canal
        sale_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sale_value = 1  # Substitua pelo valor real da revenda, se necessário
        buyer_username = "comprador_teste_revenda"  # Substitua pelo nome de usuário do revendedor
        buyer_name = "Nome Teste Revenda"  # Substitua pelo nome real do revendedor

        financial_message = (
            f"🎉 *Detalhes da Revenda* 🎉\n\n"
            f"🗓 *Data da Venda:* {sale_date}\n"
            f"💵 *Valor:* R$ {sale_value:.2f}\n"
            f"👤 *Comprador:* {buyer_username}\n"
            f"📛 *Nome:* {buyer_name}\n\n"
            "Revendedor criado com sucesso!"
        )
        notify_telegram(financial_message)
        logger.info(financial_message)

        return success_message
    else:
        error_message = f"Erro ao criar revendedor: {result}"
        notify_telegram(error_message)
        logger.error(error_message)
        return error_message

# Função de comando do Telegram para criar revendedor
async def create_reseller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /createreseller command")
    
    # Gerar usuário e senha aleatórios
    username = generate_random_string(6)
    password = generate_random_string(6)
    
    # Criar o revendedor
    reseller_info = create_reseller(username=username, password=password)
    
    # Verificar se é um comando ou um callback query
    if update.message:
        await update.message.reply_text(reseller_info, parse_mode="Markdown", disable_web_page_preview=True)
    elif update.callback_query:
        await update.callback_query.edit_message_text(reseller_info, parse_mode="Markdown", disable_web_page_preview=True)
