#config.py
import os

# Configurações e variáveis de ambiente
API_KEY = os.getenv('TELEGRAM_API_KEY', '7297529152:AAGxWksMJynOnC1iUZLFAHuKBwdxyXoEclQ')
IOS_API_KEY = os.getenv('IOS_API_KEY', 'qrk9drkGiwdcESg0GMcegQIfK0')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002225678009')
DEFAULT_VALIDITY_DAYS = 30  # Validade padrão de 30 dias
DEFAULT_USER_LIMIT = 1  # Limite padrão de 1 conexão
DEFAULT_RESELLER_LIMIT = 10  # Limite padrão de 10 conexões para revendedores
