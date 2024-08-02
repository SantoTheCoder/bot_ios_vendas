import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from users import simulate_sale, create_user_command
from resellers import create_reseller_command

logger = logging.getLogger(__name__)

# Função para criar o menu principal
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Displaying the main menu")
    
    # Definindo os botões inline com emojis e colocando um abaixo do outro
    keyboard = [
        [InlineKeyboardButton("📱 Adquirir Plano iOS", callback_data='adquirir_plano')],
        [InlineKeyboardButton("🤝 Tornar-se Revendedor iOS", callback_data='tornar_revendedor')],
        [InlineKeyboardButton("💼 Afiliado", callback_data='afiliado')],
        [InlineKeyboardButton("🛠️ Suporte", callback_data='suporte')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Bem-vindo ao Bot de Vendas para iOS! Por favor, escolha uma das opções abaixo:",
        reply_markup=reply_markup
    )

# Função para lidar com os botões pressionados
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'adquirir_plano':
        # Simula a venda do usuário e envia as informações para o usuário
        user = simulate_sale()
        if user:
            message = (
                "🎉 *Usuário Criado com Sucesso\\!* 🎉\n\n"
                f"🔎 *Usuário:* `{user['username']}`\n\n"
                f"🔑 *Senha:* `{user['password']}`\n\n"
                f"🎯 *Validade:* `{user['validity_date']}`\n\n"
                f"🕟 *Limite de Conexões:* `{user['limit']}`\n\n"
                "📱 *Aplicativos e Arquivos de Configuração:*\n\n"
                "\\- *Para iOS:*\n"
                "  \\- *Aplicativo:* [Baixe aqui](https://apps.apple.com/us/app/npv-tunnel/id1629465476)\n"
                "  \\- *Arquivos de Configuração:* [Clique aqui](https://t.me/+R72mmGw8JMdiZWEx)\n\n"
                "\\- *Para Android:*\n"
                "  \\- *Aplicativo:* [Baixe aqui](https://www.mediafire.com/file/4l22uh78g37o1yl/Poison+5g\\-DT.apk/file)\n\n"
                "🌍 *Link de Renovação:*\n"
                "[Renove aqui](https://poisonbrasil.atlasssh.com/renovar.php)\n"
                "_\\(Use este link para realizar suas renovações futuras\\)_"
            )
            await query.edit_message_text(message, parse_mode="MarkdownV2", disable_web_page_preview=True)
        else:
            await query.edit_message_text("Erro ao criar usuário. Tente novamente mais tarde.", parse_mode="MarkdownV2")

    elif query.data == 'tornar_revendedor':
        # Cria um revendedor e envia as informações para o usuário
        await create_reseller_command(update, context)
    
    elif query.data == 'afiliado':
        await query.edit_message_text("Você escolheu *Afiliado*. Mais informações em breve!", parse_mode="MarkdownV2")
    
    elif query.data == 'suporte':
        await query.edit_message_text("Você escolheu *Suporte*. Mais informações em breve!", parse_mode="MarkdownV2")
