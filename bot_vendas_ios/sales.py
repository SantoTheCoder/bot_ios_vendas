#sales.py
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
            sale_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sale_value = 1  # Substitua pelo valor real da venda
            buyer_username = user['username']  # O nome de usuário do comprador
            buyer_name = "Nome Teste"  # Substitua pelo nome real do comprador
            
            # Mensagem detalhada enviada ao canal
            sale_message = (
                "🎉 *Usuário Criado com Sucesso!* 🎉\n\n"
                f"🗓 *Data da Venda:* {sale_date}\n"
                f"💵 *Valor:* R$ {sale_value:.2f}\n"
                f"👤 *Comprador:* {buyer_username}\n"
                f"📛 *Nome:* {buyer_name}\n\n"
                f"🔎 *Usuário:*\n`{user['username']}`\n\n"
                f"🔑 *Senha:*\n`{user['password']}`\n\n"
                f"🎯 *Validade:*\n`{user['validity_date']}`\n\n"
                f"🕟 *Limite de Conexões:*\n`{user['limit']}`\n\n"
                "📱 *Aplicativos e Arquivos de Configuração:*\n\n"
                "- *Para iOS:*\n"
                "  - *Aplicativo:* [Baixe aqui](https://apps.apple.com/us/app/npv-tunnel/id1629465476)\n"
                "  - *Arquivos de Configuração:* [Clique aqui](https://t.me/+R72mmGw8JMdiZWEx)\n\n"
                "- *Para Android:*\n"
                "  - *Aplicativo:* [Baixe aqui](https://www.mediafire.com/file/4l22uh78g37o1yl/Poison+5g+-+DT.apk/file)\n\n"
                "🌍 *Link de Renovação:*\n"
                "[Renove aqui](https://poisonbrasil.atlasssh.com/renovar.php)\n"
                "*Use este link para realizar suas renovações futuras.*"
            )
            # Enviar a mensagem ao canal
            notify_telegram(sale_message)
            return sale_message
        else:
            return "Erro ao renovar a validade do usuário. Por favor, verifique manualmente."
    else:
        return "Nenhum usuário disponível para venda no momento."
