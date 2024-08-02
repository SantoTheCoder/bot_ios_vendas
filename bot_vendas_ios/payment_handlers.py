from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from mercadopago import gerar_qr_code_mercado_pago, mp, verificar_pagamento_pix
import logging
import asyncio
import base64
from datetime import datetime  # Importar datetime para obter a data da compra
from users import distribute_user  # Importando a função de distribuição de usuário
from resellers import create_reseller  # Importando a função de criação de revendedor
from notifications import notify_telegram  # Importando a função de notificação

logger = logging.getLogger(__name__)

planos = {
    'usuario': {
        'nome': 'Plano 1 Pessoa',
        'preco': 1,  # Ajustar o preço correto
        'tipo': 'usuario',
    },
    'revenda_10': {
        'nome': 'Revenda iOS - 10 Pessoas',
        'preco': 1,  # Valor de R$ 1,00
        'tipo': 'revenda',
        'limite': 10,
    },
    'revenda_20': {
        'nome': 'Revenda iOS - 20 Pessoas',
        'preco': 1,  # Valor de R$ 1,00
        'tipo': 'revenda',
        'limite': 20,
    },
    'revenda_50': {
        'nome': 'Revenda iOS - 50 Pessoas',
        'preco': 1,  # Valor de R$ 1,00
        'tipo': 'revenda',
        'limite': 50,
    }
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
        limite = plano_info.get('limite', None)  # Usa 'None' se não houver 'limite'

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
                f"Aqui está o código Pix para pagamento:\n\n`{qr_code}`"
            )
            await query.message.reply_text(text=message, parse_mode='Markdown')
            logger.info(f"QR Code enviado para o usuário {query.message.chat_id}")

            # Iniciar a verificação de pagamento
            asyncio.create_task(verificar_pagamento_pix(mp, qr_code_data['id'], query.message.chat.id, context, tipo, limite))

async def process_successful_payment(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tipo: str, preco_final: float, limite: int):
    data_compra = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    chat_info = await context.bot.get_chat(chat_id)  # Aguarda a chamada assíncrona
    nome_comprador = chat_info.first_name
    id_comprador = chat_id

    if tipo == "usuario":
        user = distribute_user()  # Distribui um usuário existente
        if user:
            # Mensagem enviada ao comprador
            user_message = (
                "🎉 **Usuário Criado com Sucesso!** 🎉\n\n"
                f"🔎 **Usuário:**\n`{user['username']}`\n\n"
                f"🔑 **Senha:**\n`{user['password']}`\n\n"
                f"🎯 **Validade:**\n`{user['validity_date']}`\n\n"
                f"🕟 **Limite de Conexões:**\n`{user['limit']}`\n\n"
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
            await context.bot.send_message(chat_id=chat_id, text=user_message, parse_mode="Markdown", disable_web_page_preview=True)
            logger.info(f"Mensagem de usuário enviada para {chat_id}")

            # Mensagem enviada ao canal com informações financeiras
            canal_message = (
                user_message +  # Adiciona a mensagem sem as informações financeiras
                f"\n\n💵 **Valor:** R$ {preco_final:.2f}\n"
                f"📅 **Data da Compra:** {data_compra}\n"
                f"👤 **Comprador:** {nome_comprador} (ID: {id_comprador})"
            )

            # Notificar e fixar a mensagem no canal
            notify_telegram(canal_message, pin_message=True)

    elif tipo == "revenda" and limite:
        reseller_info = create_reseller(limit=limite)  # Cria um novo revendedor com a cota específica
        if reseller_info:
            # Mensagem enviada ao comprador
            reseller_message = (
                reseller_info +
                f"\n\n💵 **Valor:** R$ {preco_final:.2f}\n"
                f"📅 **Data da Compra:** {data_compra}\n"
                f"👤 **Comprador:** {nome_comprador} (ID: {id_comprador})"
            )
            await context.bot.send_message(chat_id=chat_id, text=reseller_info, parse_mode="Markdown", disable_web_page_preview=True)
            logger.info(f"Mensagem de revendedor enviada para {chat_id}")

            # Notificar e fixar a mensagem no canal
            notify_telegram(reseller_message, pin_message=True)

async def verificar_pagamento_pix(mp, id_pagamento, chat_id, context, tipo, limite: int):
    while True:
        logger.info(f"Verificando pagamento {id_pagamento}...")
        pagamento_info = mp.get_pagamento(id_pagamento)
        status = pagamento_info.get('status')
        logger.info(f"Status do pagamento {id_pagamento}: {status}")
        if status == 'approved':
            await process_successful_payment(chat_id, context, tipo, 1.00, limite)
            break
        await asyncio.sleep(60)  # Verificar a cada 60 segundos
