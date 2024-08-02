#menu.py
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
        [InlineKeyboardButton("💼 Tornar-se Revendedor iOS", callback_data='revenda')],
        [InlineKeyboardButton("🎯 Afiliado", callback_data='afiliado')],
        [InlineKeyboardButton("🆘 Suporte", callback_data='suporte')]
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
    
    if query.data in ['usuario', 'revenda']:
        await process_payment(update, context)  # Processo de pagamento
    elif query.data == 'afiliado':
        await query.edit_message_text("Você escolheu *Afiliado*. Mais informações em breve!", parse_mode="MarkdownV2")
    elif query.data == 'suporte':
        await query.edit_message_text("Você escolheu *Suporte*. Mais informações em breve!", parse_mode="MarkdownV2")