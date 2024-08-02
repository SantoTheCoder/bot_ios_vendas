import logging
from datetime import datetime, timedelta
from users import distribute_user
from notifications import notify_telegram
from utils import make_request
from config import IOS_API_KEY, DEFAULT_VALIDITY_DAYS

logger = logging.getLogger(__name__)

def renew_user(username, days_to_extend):
    data = {
        'passapi': IOS_API_KEY,
        'module': 'renewuser',
        'user': username,
        'validadeusuario': days_to_extend
    }

    result = make_request(data)
    if 'error' not in result:
        logger.info(f"Usuário {username} renovado com sucesso por {days_to_extend} dias.")
        return True
    else:
        logger.error(f"Erro ao renovar usuário {username}: {result}")
        return False

def process_sale():
    user = distribute_user()
    if user:
        # Calcula quantos dias se passaram desde a criação
        creation_date = datetime.strptime(user['validity_date'], "%d/%m/%Y") - timedelta(days=DEFAULT_VALIDITY_DAYS)
        days_since_creation = (datetime.now() - creation_date).days

        # Calcula os dias a renovar para garantir 30 dias completos
        days_to_extend = DEFAULT_VALIDITY_DAYS - days_since_creation

        renewed = renew_user(user['username'], days_to_extend)
        if renewed:
            sale_message = (
                "🎉 *Usuário Vendido* 🎉\n\n"
                f"🔎 *Usuário:* `{user['username']}`\n"
                f"🔑 *Senha:* `{user['password']}`\n"
                f"🎯 *Validade:* 30 dias\n\n"
                "Obrigado por sua compra!"
            )
            notify_telegram(sale_message)
            return sale_message
        else:
            return "Erro ao renovar a validade do usuário. Por favor, verifique manualmente."
    else:
        return "Nenhum usuário disponível para venda no momento."
