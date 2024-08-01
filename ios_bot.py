import logging
import requests
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuração básica de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class IOSBot:
    def __init__(self, api_key, telegram_bot_token, telegram_chat_id, default_validity_days=30):
        self.api_key = api_key
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.default_validity_days = default_validity_days
        self.base_url = 'https://poisonbrasil.atlasssh.com/core/apiatlas.php'  # URL da API correta
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def make_request(self, data):
        logger.info("Sending request to API with data: %s", data)
        try:
            response = requests.post(self.base_url, headers=self.headers, data=data)
            logger.info("Response received: %s", response.text)
            return response.json()
        except Exception as e:
            logger.error("Error during API request: %s", e)
            return {"error": str(e)}

    def generate_random_string(self, length=8):
        random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        logger.info("Generated random string: %s", random_string)
        return random_string

    def notify_telegram(self, message, chat_id=None, disable_preview=True):
        logger.info("Sending message to Telegram: %s", message)
        if chat_id is None:
            chat_id = self.telegram_chat_id
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': "Markdown",
                'disable_web_page_preview': disable_preview
            }
            response = requests.post(url, data=data)
            logger.info("Message sent. Response: %s", response.text)
        except Exception as e:
            logger.error("Error sending message to Telegram: %s", e)

    def create_user(self, limit, username=None, password=None):
        logger.info("Creating user with limit: %d", limit)
        if username is None:
            username = self.generate_random_string()
        if password is None:
            password = self.generate_random_string()

        data = {
            'passapi': self.api_key,
            'module': 'criaruser',
            'user': username,
            'pass': password,
            'admincid': 1,  # ID da categoria, ajuste conforme necessário
            'validadeusuario': self.default_validity_days,
            'userlimite': limit
        }
        result = self.make_request(data)

        if 'error' not in result:
            success_message = (
                "🎉 *Usuário Criado* 🎉\n\n"
                "🔎 *Usuário:*\n"
                f"`{username}`\n\n"
                "🔑 *Senha:*\n"
                f"`{password}`\n\n"
                "🎯 *Validade:*\n"
                "30/08/2024\n\n"
                "🕟 *Limite:*\n"
                f"{limit}\n\n"
                "[📱 *APLICATIVOS (Clique Aqui)*](https://apps.apple.com/us/app/npv-tunnel/id1629465476)\n"
                "[📁 *ARQUIVOS (Clique Aqui)*](https://t.me/+R72mmGw8JMdiZWEx)\n\n"
                "🌍 [*Link de Renovação (Clique Aqui)*](https://poisonbrasil.atlasssh.com/renovar.php)\n\n"
                "Suporte: @Pedrooo\n\n"
                "_Esse link servirá para você fazer as suas renovações_"
            )
            # Enviar para o canal e para o usuário
            self.notify_telegram(success_message, chat_id=self.telegram_chat_id)
            logger.info(success_message)
            return success_message
        else:
            error_message = f"Erro ao criar usuário: {result}"
            self.notify_telegram(error_message, chat_id=self.telegram_chat_id)
            logger.error(error_message)
            return error_message

    def create_reseller(self, limit, username=None, password=None):
        logger.info("Creating reseller with limit: %d", limit)
        if username is None:
            username = self.generate_random_string()
        if password is None:
            password = self.generate_random_string()

        data = {
            'passapi': self.api_key,
            'module': 'createrev',
            'user': username,
            'pass': password,
            'admincid': 1,  # ID da categoria, ajuste conforme necessário
            'userlimite': limit,
        }
        result = self.make_request(data)

        if 'error' not in result:
            success_message = (
                "🎉 *Revendedor Criado* 🎉\n\n"
                "🔎 *Usuário:*\n"
                f"`{username}`\n\n"
                "🔑 *Senha:*\n"
                f"`{password}`\n\n"
                "🎯 *Validade:*\n"
                "30/08/2024\n\n"
                "🕟 *Limite:*\n"
                f"{limit}\n\n"
                "💥 Obrigado por usar nossos serviços!\n\n"
                "🔗 [*Link do Painel (Clique Aqui)*](https://poisonbrasil.atlasssh.com/)\n\n"
                "Suporte: @Pedrooo"
            )
            # Enviar para o canal e para o usuário
            self.notify_telegram(success_message, chat_id=self.telegram_chat_id)
            logger.info(success_message)
            return success_message
        else:
            error_message = f"Erro ao criar revendedor: {result}"
            self.notify_telegram(error_message, chat_id=self.telegram_chat_id)
            logger.error(error_message)
            return error_message

# Configuração do bot Telegram e API do painel
API_KEY = '7297529152:AAGxWksMJynOnC1iUZLFAHuKBwdxyXoEclQ'
IOS_API_KEY = 'quafJv1C6i8FI4WKAMB9SnLnDn'  # Nova senha da API
TELEGRAM_CHAT_ID = '-1002225678009'  # ID do canal ou grupo do Telegram
ios_bot = IOSBot(IOS_API_KEY, API_KEY, TELEGRAM_CHAT_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bem-vindo ao Bot de Vendas!')

async def create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = 1  # Defina o limite padrão para 1 conexão
    message = ios_bot.create_user(limit=limit)
    await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)

async def create_reseller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = 10  # Defina o limite padrão para revendedores
    message = ios_bot.create_reseller(limit=limit)
    await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("createuser", create_user))
    application.add_handler(CommandHandler("createreseller", create_reseller))

    logger.info("Starting the bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
