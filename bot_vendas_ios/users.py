#users.py
import json
import random
import string
import logging
import os
from datetime import datetime, timedelta
from config import DEFAULT_VALIDITY_DAYS, DEFAULT_USER_LIMIT, IOS_API_KEY
from utils import make_request
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

USERS_FILE = 'bot_vendas_ios/users.json'
USERS_DIR = os.path.dirname(USERS_FILE)

def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_users(users):
    os.makedirs(USERS_DIR, exist_ok=True)
    
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

def create_users(number_of_users):
    users = load_users()
    new_users = []

    for _ in range(number_of_users):
        username = generate_random_string(8)
        password = generate_random_string(8)
        creation_date = datetime.now().strftime("%d/%m/%Y")
        validity_date = (datetime.now() + timedelta(days=DEFAULT_VALIDITY_DAYS)).strftime("%d/%m/%Y")
        
        user_data = {
            'username': username,
            'password': password,
            'creation_date': creation_date,  # Adiciona a data de criação
            'validity_date': validity_date,
            'limit': DEFAULT_USER_LIMIT,
            'activated': False,
            'v2ray': "NÃO",
            'whatsapp': "1234567890",
            'notas': "",
            'sale_date': None  # Inicialmente, sem data de venda
        }

        api_data = {
            'passapi': IOS_API_KEY,
            'module': 'criaruser',
            'user': username,
            'pass': password,
            'validadeusuario': DEFAULT_VALIDITY_DAYS,
            'userlimite': DEFAULT_USER_LIMIT,
            'whatsapp': user_data['whatsapp']
        }

        result = make_request(api_data)

        if 'error' not in result:
            users.append(user_data)
            new_users.append(user_data)
            logger.info(f'Usuário {username} criado e armazenado com sucesso.')
        else:
            logger.error(f'Erro ao criar o usuário {username}: {result}')

    save_users(users)
    return new_users

def get_active_users():
    users = load_users()
    active_users = [user for user in users if user['activated']]
    return active_users

def get_inactive_users():
    users = load_users()
    inactive_users = [user for user in users if not user['activated']]
    return inactive_users

def activate_user(username):
    users = load_users()
    for user in users:
        if user['username'] == username and not user['activated']:
            user['activated'] = True
            user['sale_date'] = datetime.now().strftime("%d/%m/%Y")
            
            # Recalcular a data de validade com base na data de criação
            creation_date = datetime.strptime(user['creation_date'], "%d/%m/%Y")
            days_since_creation = (datetime.now() - creation_date).days
            new_validity_date = (creation_date + timedelta(days=DEFAULT_VALIDITY_DAYS)).strftime("%d/%m/%Y")
            user['validity_date'] = new_validity_date
            
            save_users(users)
            logger.info(f'Usuário {username} ativado em {user["sale_date"]} com validade até {user["validity_date"]}.')
            return user
    return None

def distribute_user():
    inactive_users = get_inactive_users()
    if inactive_users:
        user = inactive_users.pop(0)
        activated_user = activate_user(user["username"])  # Certifica-se de ativar o usuário
        logger.info(f'Usuário {user["username"]} distribuído.')
        return activated_user
    else:
        logger.warning('Nenhum usuário inativo disponível para distribuição.')
        return None

def simulate_sale():
    user = distribute_user()
    if user:
        logger.info(f'Simulação de venda realizada com sucesso para o usuário {user["username"]}.')
        return user
    else:
        logger.warning('Nenhum usuário disponível para simulação de venda.')
        return None

# Função de comando do Telegram para criar usuários
async def create_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /createuser command")
    new_users = create_users(10)
    user_list = "\n".join([f"Usuário: {user['username']} - Senha: {user['password']}" for user in new_users])
    await update.message.reply_text(f"10 novos usuários criados:\n\n{user_list}", parse_mode="Markdown", disable_web_page_preview=True)