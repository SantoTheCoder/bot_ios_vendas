import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payment_handlers import process_payment
from affiliate_system import affiliate_dashboard, create_affiliate_link, get_affiliate_stats  # Importa as funções necessárias

logger = logging.getLogger(__name__)

# Função para criar o menu principal
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Displaying the main menu")

    # Definindo os botões inline
    keyboard = [
        [InlineKeyboardButton("🛒 Internet Ilimitada iOS", callback_data='usuario')],
        [InlineKeyboardButton("💼 Revender iOS", callback_data='revenda_menu')],
        [InlineKeyboardButton("🎯 Afiliado", callback_data='afiliado')],
        [InlineKeyboardButton("🆘 Suporte", url='https://t.me/pedrooo')],  # Adicionando o link para o suporte
        [InlineKeyboardButton("❤️ Comprar Seguidores, Views, Likes", url='https://t.me/crescimentosocial_bot')]  # Adicionando o botão de seguidores
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Verifica se é uma mensagem normal ou um callback query
    if update.message:
        await update.message.reply_text(
            "Bem-vindo ao Bot de Vendas para iOS! Por favor, escolha uma das opções abaixo:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            "Bem-vindo ao Bot de Vendas para iOS! Por favor, escolha uma das opções abaixo:",
            reply_markup=reply_markup
        )

# Função para criar o sub-menu de revenda
async def revenda_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Displaying the reseller menu")
    
    # Definindo os botões inline do sub-menu de revenda
    keyboard = [
        [InlineKeyboardButton("💼 Revenda iOS - 10 Pessoas", callback_data='revenda_10')],
        [InlineKeyboardButton("💼 Revenda iOS - 20 Pessoas", callback_data='revenda_20')],
        [InlineKeyboardButton("💼 Revenda iOS - 50 Pessoas", callback_data='revenda_50')],
        [InlineKeyboardButton("📦 Material para Revenda", url='https://t.me/BANNERS_NET_ILIMITADA')],
        [InlineKeyboardButton("⬅️ Voltar", callback_data='start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.edit_text(
        "Escolha uma das opções de revenda abaixo:",
        reply_markup=reply_markup
    )

# Função para lidar com o painel de afiliação
async def affiliate_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Displaying affiliate dashboard")
    user_id = update.effective_user.id
    link = create_affiliate_link(user_id)
    stats = get_affiliate_stats(user_id)
    
    message = (
        f"*Receba um usuário de 30 dias sobre qualquer compra de seu afiliado:*\n\n"
        f"✅ *Total de indicados:* `{stats['total_referred']}`\n"
        f"🔎 *Último indicado:* `{stats['last_referred_user']}`\n"
        f"⌛ *Horário:* `{stats['last_referred_time']}`\n\n"
        f"🔗 *Seu Link:* `{link}`"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data='start')]  # Botão "Voltar ao Menu" apontando para 'start'
    ]
    
    if update.message:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# Função para lidar com os botões pressionados
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.debug(f"Callback data received: {query.data}")

    if query.data == 'usuario':
        logger.debug("Processing payment for 'usuario'")
        await process_payment(update, context)  # Processo de pagamento
    elif query.data == 'revenda_menu':
        logger.debug("Displaying reseller menu")
        await revenda_menu(update, context)  # Exibe o sub-menu de revenda
    elif query.data in ['revenda_10', 'revenda_20', 'revenda_50']:
        logger.debug(f"Processing payment for {query.data}")
        await process_payment(update, context)  # Processo de pagamento para diferentes planos de revenda
    elif query.data == 'afiliado':
        logger.debug("Displaying affiliate dashboard")
        await affiliate_dashboard(update, context)  # Exibe o painel de afiliação
    elif query.data == 'suporte':
        logger.debug("Displaying support message")
        await query.edit_message_text("Você escolheu *Suporte*. Mais informações em breve!", parse_mode="Markdown")
    elif query.data == 'start':
        logger.debug("Returning to main menu")
        await start_command(update, context)  # Volta ao menu principal
