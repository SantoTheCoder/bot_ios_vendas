from telegram import Update, InlineKeyboardButton, InputFile
from telegram.ext import ContextTypes
from mercadopago import gerar_qr_code_mercado_pago, mp, verificar_pagamento_pix
import logging
import asyncio
import base64
from datetime import datetime, timedelta
from users import distribute_users
from resellers import create_reseller
from notifications import notify_telegram
import json
import os
import requests
from config import IOS_API_KEY
from affiliate_system import record_affiliate_purchase
import sqlite3

logger = logging.getLogger(__name__)

REVENDERS_FILE = 'revendedores.json'

# Funções para carregar e salvar dados dos revendedores
def load_revendores():
    if os.path.exists(REVENDERS_FILE):
        with open(REVENDERS_FILE, 'r') as file:
            try:
                data = json.load(file)
                if isinstance(data, dict) and "revendedores" in data:
                    return data
                else:
                    return {"revendedores": {}} 
            except json.JSONDecodeError:
                return {"revendedores": {}}
    return {"revendedores": {}}

def save_revendores(data):
    with open(REVENDERS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def renovar_revendedor_painel(username):
    url = "https://poisonbrasil.atlasssh.com/core/apiatlas.php"
    data = {
        'passapi': IOS_API_KEY,
        'module': 'renewrev',
        'user': username
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        logger.info(f"Revendedor {username} renovado com sucesso no painel.")
        return response.text
    else:
        logger.error(f"Erro ao renovar revendedor {username} no painel: {response.text}")
        return None

planos = {
    'usuario': {
        'nome': 'Plano 1 Pessoa',
        'preco': 1,
        'tipo': 'usuario',
        'usuarios_entregues': 1
    },
    'usuario_2': {
        'nome': 'Plano 2 Pessoas',
        'preco': 2,
        'tipo': 'usuario',
        'usuarios_entregues': 2
    },
    'revenda_10': {
        'nome': 'Revenda iOS - 10 Pessoas',
        'preco': 1,
        'tipo': 'revenda',
        'limite': 10,
    },
    'revenda_20': {
        'nome': 'Revenda iOS - 20 Pessoas',
        'preco': 1,
        'tipo': 'revenda',
        'limite': 20,
    },
    'revenda_50': {
        'nome': 'Revenda iOS - 50 Pessoas',
        'preco': 1,
        'tipo': 'revenda',
        'limite': 50,
    }
}

def salvar_qr_code_base64(qr_code_base64: str, file_path: str) -> None:
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(qr_code_base64))

def register_sale(chat_id, sale_type, amount, buyer_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO sales (sale_date, sale_type, amount, buyer_id, buyer_name)
        VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sale_type, amount, chat_id, buyer_name))
        
        conn.commit()
        logger.info(f"Venda registrada para {buyer_name} (ID: {chat_id}), Tipo: {sale_type}, Valor: {amount}, Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Erro ao registrar a venda para {buyer_name} (ID: {chat_id}): {e}")
    finally:
        conn.close()

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plano_selecionado = query.data

    plano_info = planos.get(plano_selecionado)

    if plano_info:
        preco_final = plano_info['preco']
        tipo = plano_info['tipo']
        limite = plano_info.get('limite', None)
        usuarios_entregues = plano_info.get('usuarios_entregues', 1)

        # Definindo as informações do pagador (payer_info)
        payer_info = {
            "email": "poison@gmail.com",
            "first_name": "IOS 4G",
            "last_name": "Ilimitado",
            "identification": {
                "type": "CPF",
                "number": "08005204833"  # Substitua pelo CPF real do pagador
            }
        }

        # Agora passamos o payer_info para a função gerar_qr_code_mercado_pago
        qr_code_data = gerar_qr_code_mercado_pago(preco_final, payer_info)

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

            asyncio.create_task(verificar_pagamento_pix(mp, qr_code_data['id'], query.message.chat.id, context, tipo, limite, usuarios_entregues))

async def process_successful_payment(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tipo: str, preco_final: float, limite: int, usuarios_entregues: int):
    data_compra = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    chat_info = await context.bot.get_chat(chat_id)
    nome_comprador = chat_info.first_name
    id_comprador = chat_id

    # Registro da venda no banco de dados
    register_sale(chat_id, tipo, preco_final, nome_comprador)

    revendedores = load_revendores()

    if tipo == "usuario":
        users = distribute_users(usuarios_entregues)
        if users:
            for user in users:
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

            canal_message = (
                user_message +  
                f"\n\n💵 **Valor:** R$ {preco_final:.2f}\n"
                f"📅 **Data da Compra:** {data_compra}\n"
                f"👤 **Comprador:** {nome_comprador} (ID: {id_comprador})"
            )
            notify_telegram(canal_message, pin_message=True)

    elif tipo == "revenda" and limite:
        if str(chat_id) in revendedores["revendedores"]:
            reseller_info = revendedores["revendedores"][str(chat_id)]
            username = reseller_info["username"]

            resultado_renovacao = renovar_revendedor_painel(username)
            if resultado_renovacao:
                validade_antiga = datetime.strptime(reseller_info["validade"], "%d/%m/%Y")
                nova_validade = (validade_antiga + timedelta(days=30)).strftime("%d/%m/%Y")
                reseller_info["validade"] = nova_validade
                reseller_info["data_compra"] = data_compra

                save_revendores(revendedores)

                reseller_message = (
                    f"🔄 *Renovação de Revendedor* 🔄\n\n"
                    f"🔎 *Revendedor:* `{username}`\n"
                    f"📅 *Nova Validade:* {nova_validade}\n"
                )
            else:
                reseller_message = "Erro ao renovar revendedor no painel. Por favor, tente novamente mais tarde."
        else:
            reseller_info = create_reseller(limit=limite)
            if reseller_info:
                username = reseller_info.split("`")[1]
                validade = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
                revendedores["revendedores"][str(chat_id)] = {
                    "username": username,
                    "limite": limite,
                    "data_compra": data_compra,
                    "validade": validade
                }
                save_revendores(revendedores)

                reseller_message = (
                    reseller_info
                )

        await context.bot.send_message(chat_id=chat_id, text=reseller_message, parse_mode="Markdown", disable_web_page_preview=True)
        logger.info(f"Mensagem de revendedor enviada para {chat_id}")

        canal_message = (
            reseller_message +
            f"\n\n💵 **Valor:** R$ {preco_final:.2f}\n"
            f"📅 **Data da Compra:** {data_compra}\n"
            f"👤 **Comprador:** {nome_comprador} (ID: {id_comprador})"
        )

        notify_telegram(canal_message, pin_message=True)

    # Registro da compra do afiliado
    referrer_id = context.user_data.get('referrer_id')
    if referrer_id:
        logger.info(f"Registrando compra do usuário {chat_id} referenciado pelo afiliado {referrer_id}")
        await record_affiliate_purchase(referrer_id, chat_id, context)

async def verificar_pagamento_pix(mp, id_pagamento, chat_id, context, tipo, limite: int, usuarios_entregues: int):
    while True:
        logger.info(f"Verificando pagamento {id_pagamento}...")
        pagamento_info = mp.get_pagamento(id_pagamento)
        status = pagamento_info.get('status')
        logger.info(f"Status do pagamento {id_pagamento}: {status}")
        if status == 'approved':
            await process_successful_payment(chat_id, context, tipo, 1.00, limite, usuarios_entregues)
            break
        await asyncio.sleep(60)
