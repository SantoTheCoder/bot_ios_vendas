#payment_handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from mercadopago import gerar_qr_code_mercado_pago, mp, verificar_pagamento_pix
import random
import logging
import asyncio
import base64
from users import distribute_user  # Importando a função de distribuição de usuário
from resellers import create_reseller  # Importando a função de criação de revendedor
from notifications import notify_telegram  # Importando a função de notificação

logger = logging.getLogger(__name__)

planos = {
    'usuario': {
        'nome': 'Plano 1 Pessoa',
        'preco': 1,
        'tipo': 'usuario',
    },
    'revenda': {
        'nome': 'Revenda iOS',
        'preco': 1,
        'tipo': 'revenda',
    },
}

def salvar_qr_code_base64(qr_code_base64: str, file_path: str) -> None:
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(qr_code_base64))

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plano_selecionado = query.data

    plano_info = planos.get(plano_selecionado)

    if plano_info:
        preco_final = plano_info['preco']
        tipo = plano_info['tipo']

        qr_code_data = gerar_qr_code_mercado_pago(preco_final)

        if not qr_code_data:
            message = "Erro ao obter o QR Code."
            await query.edit_message_text(text=message)
        else:
            qr_code = qr_code_data['qr_code']
            qr_code_base64 = qr_code_data['qr_code_base64']
            image_path = f"qrcodes/{plano_selecionado}.png"
            salvar_qr_code_base64(qr_code_base64, image_path)

            with open(image_path, 'rb') as qr_image:
                await query.message.reply_photo(photo=InputFile(qr_image), caption="Escaneie o QR code para pagar.")

            message = (
                f"Você selecionou o {plano_info['nome']} - R$ {preco_final:.2f}.\n\n"
                f"Aqui está o código Pix para pagamento:\n\n{qr_code}"
            )
            await query.message.reply_text(text=message, parse_mode='Markdown')
            logger.info(f"QR Code enviado para o usuário {query.message.chat_id}")

            # Iniciar a verificação de pagamento
            asyncio.create_task(verificar_pagamento_pix(mp, qr_code_data['id'], query.message.chat.id, context, tipo))

async def process_successful_payment(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tipo: str):
    if tipo == "usuario":
        user = distribute_user()  # Distribui um usuário existente
        if user:
            message = (
                "🎉 **Usuário Criado com Sucesso!** 🎉\n\n"
                f"🔎 **Usuário:**\n{user['username']}\n\n"
                f"🔑 **Senha:**\n{user['password']}\n\n"
                f"🎯 **Validade:**\n{user['validity_date']}\n\n"  # Corrigido aqui
                f"🕟 **Limite de Conexões:**\n{user['limit']}\n\n"
                "📱 **Aplicativos e Arquivos de Configuração:**\n\n"
                "- **Para iOS:**\n"
                "  - **Aplicativo:** [Baixe aqui](https://apps.apple.com/us/app/npv-tunnel/id1629465476)\n"
                "  - **Arquivos de Configuração:** [Clique aqui](https://t.me/+R72mmGw8JMdiZWEx)\n\n"
                "- **Para Android:**\n"
                "  - **Aplicativo:** [Baixe aqui](https://www.mediafire.com/file/4l22uh78g37o1yl/Poison+5g+-+DT.apk/file)\n\n"
                "🌍 **Link de Renovação:**\n"
                "[Renove aqui](https://poisonbrasil.atlasssh.com/renovar.php)\n"
                "*Use este link para realizar suas renovações futuras.*"
            )
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)
            logger.info(f"Mensagem de usuário enviada para {chat_id}")

            # Notificar e fixar a mensagem no canal
            notify_telegram(message, pin_message=True)

    elif tipo == "revenda":
        reseller_info = create_reseller()  # Cria um novo revendedor
        if reseller_info:
            await context.bot.send_message(chat_id=chat_id, text=reseller_info, parse_mode="Markdown", disable_web_page_preview=True)
            logger.info(f"Mensagem de revendedor enviada para {chat_id}")

            # Notificar e fixar a mensagem no canal
            notify_telegram(reseller_info, pin_message=True)

async def verificar_pagamento_pix(mp, id_pagamento, chat_id, context, tipo):
    while True:
        logger.info(f"Verificando pagamento {id_pagamento}...")
        pagamento_info = mp.get_pagamento(id_pagamento)
        status = pagamento_info.get('status')
        logger.info(f"Status do pagamento {id_pagamento}: {status}")
        if status == 'approved':
            await process_successful_payment(chat_id, context, tipo)
            break
        await asyncio.sleep(60)  # Verificar a cada 60 segundos