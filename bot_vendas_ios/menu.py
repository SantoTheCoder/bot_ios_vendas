import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payment_handlers import process_payment

logger = logging.getLogger(__name__)

# Função para criar o menu principal
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Displaying the main menu")
    
    # Definindo os botões inline
    keyboard = [
        [InlineKeyboardButton("🛒 Adquirir Plano iOS", callback_data='usuario')],
        [InlineKeyboardButton("💼 Tornar-se Revendedor iOS", callback_data='revenda_menu')],
        [InlineKeyboardButton("🎯 Afiliado", callback_data='afiliado')],
        [InlineKeyboardButton("🆘 Suporte", callback_data='suporte')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
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

# Função para lidar com os botões pressionados
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'usuario':
        await process_payment(update, context)  # Processo de pagamento
    elif query.data == 'revenda_menu':
        await revenda_menu(update, context)  # Exibe o sub-menu de revenda
    elif query.data in ['revenda_10', 'revenda_20', 'revenda_50']:
        await process_payment(update, context)  # Processo de pagamento para diferentes planos de revenda
    elif query.data == 'afiliado':
        await query.edit_message_text("Você escolheu *Afiliado*. Mais informações em breve!", parse_mode="MarkdownV2")
    elif query.data == 'suporte':
        await query.edit_message_text("Você escolheu *Suporte*. Mais informações em breve!", parse_mode="MarkdownV2")
    elif query.data == 'start':
        await start_command(update, context)  # Volta ao menu principal

