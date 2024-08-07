import requests
import json
import uuid
import asyncio
import logging
from config import ACCESS_TOKEN
from sales_simulation import simulate_sale  # Importa a função de simulação de venda
from resellers import create_reseller_command  # Importa a função de criação de revendedor
from notifications import notify_telegram

logger = logging.getLogger(__name__)

class MercadoPago:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_pagamento(self, id_pagamento):
        return self.request(f'https://api.mercadopago.com/v1/payments/{id_pagamento}')

    def request(self, url, method='GET', data=None, headers=None):
        if headers is None:
            headers = {}
        headers['Authorization'] = f"Bearer {self.access_token}"
        headers['Content-Type'] = 'application/json'

        response = requests.request(method, url, headers=headers, data=data)
        logger.info(f"Request URL: {url}")
        logger.info(f"Request Method: {method}")
        logger.info(f"Request Data: {data}")
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Content: {response.content}")
        
        if response.status_code != 200:
            logger.error(f"Error in MercadoPago request: {response.text}")
            return None
        return response.json()

async def verificar_pagamento_pix(mp, id_pagamento, chat_id, context, tipo):
    while True:
        logger.info(f"Verificando pagamento {id_pagamento}...")
        pagamento_info = mp.get_pagamento(id_pagamento)
        status = pagamento_info.get('status')
        logger.info(f"Status do pagamento {id_pagamento}: {status}")
        
        if status == 'approved':
            if tipo == 'usuario':
                user_info = simulate_sale()  # Reutiliza a função de simulação de venda
                if user_info:
                    await context.bot.send_message(chat_id=chat_id, text=user_info, parse_mode="Markdown")
                else:
                    logger.error("Não há usuários disponíveis para distribuição.")
                    await context.bot.send_message(chat_id=chat_id, text="❌ Nenhum usuário disponível no momento. Tente novamente mais tarde.")
            elif tipo == 'revenda':
                update_dummy = type('obj', (object,), {'message': type('obj', (object,), {'reply_text': None})})()
                context_dummy = ContextTypes.DEFAULT_TYPE()
                reseller_info = await create_reseller_command(update_dummy, context_dummy)  # Reutiliza a função de criação de revendedor
                
                if reseller_info:
                    await context.bot.send_message(chat_id=chat_id, text=reseller_info, parse_mode="Markdown")
                else:
                    logger.error("Erro ao criar o revendedor.")
                    await context.bot.send_message(chat_id=chat_id, text="❌ Erro ao criar o revendedor. Tente novamente mais tarde.")
            
            logger.info(f"Pagamento {id_pagamento} aprovado e {tipo} processado com sucesso.")
            break
        
        await asyncio.sleep(60)  # Verificar a cada 60 segundos

def gerar_qr_code_mercado_pago(valor: float, payer_info: dict) -> dict:
    url = "https://api.mercadopago.com/v1/payments"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }
    payload = {
        "transaction_amount": valor,
        "description": "Pagamento com PIX",
        "payment_method_id": "pix",
        "payer": payer_info  # Dados dinâmicos do pagador
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        payment_data = response.json()
        logger.info(f"QR Code gerado com sucesso: {payment_data}")
        return {
            "id": payment_data.get('id'),
            "qr_code_base64": payment_data['point_of_interaction']['transaction_data']['qr_code_base64'],
            "qr_code": payment_data['point_of_interaction']['transaction_data']['qr_code']
        }
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
        logger.error(f"Response content: {response.content}")
        logger.error(f"Payload sent: {json.dumps(payload, indent=4)}")
    except Exception as err:
        logger.error(f"Other error occurred: {err}")
    
    return None

# Criando a instância de MercadoPago
mp = MercadoPago(ACCESS_TOKEN)

# Exemplo de uso com informações reais do pagador
payer_info = {
    "email": "poison@gmail.com",
    "first_name": "IOS 4G",
    "last_name": "Ilimitado",
    "identification": {
        "type": "CPF",
        "number": "08005204833"  # Substitua pelo CPF real do pagador
    }
}

# Geração do QR Code com informações reais do pagador
qr_code_data = gerar_qr_code_mercado_pago(valor=100.0, payer_info=payer_info)
