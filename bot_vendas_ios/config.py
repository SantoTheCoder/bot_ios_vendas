#config.py
import os

# Configurações e variáveis de ambiente
API_KEY = os.getenv('TELEGRAM_API_KEY', '7297529152:AAGxWksMJynOnC1iUZLFAHuKBwdxyXoEclQ')
IOS_API_KEY = os.getenv('IOS_API_KEY', 'qrk9drkGiwdcESg0GMcegQIfK0')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002225678009')
DEFAULT_VALIDITY_DAYS = 30  # Validade padrão de 30 dias
DEFAULT_USER_LIMIT = 1  # Limite padrão de 1 conexão
DEFAULT_RESELLER_LIMIT = 10  # Limite padrão de 10 conexões para revendedores
# Configurações do MercadoPago
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', 'APP_USR-1062519597180352-070416-90b9d92c9d0edc48f826dc34266ceb2e-585772932')
CHAVE_PIX = os.getenv('CHAVE_PIX', '28d812de-5fe9-4864-a3b2-d684e1ac4fe5')

# Adicione o nome do bot ao config.py
BOT_NAME = os.getenv('BOT_NAME', '@IOS_TESTE_BOT')

SUPPORT_CONTACT = os.getenv('SUPPORT_CONTACT', '@Pedrooo')
ADMIN_ID = '5197753914'
