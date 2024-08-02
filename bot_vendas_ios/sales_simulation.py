import logging
from telegram import Update
from telegram.ext import ContextTypes
from users import simulate_sale

logger = logging.getLogger(__name__)

async def simulate_sale_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /simulate_sale command")
    user = simulate_sale()
    if user:
        message = (
            "🎉 *Usuário Criado com Sucesso\\!* 🎉\n\n"
            f"🔎 *Usuário:*\n`{user['username']}`\n\n"
            f"🔑 *Senha:*\n`{user['password']}`\n\n"
            f"🎯 *Validade:*\n`{user['validity_date']}`\n\n"
            f"🕟 *Limite de Conexões:*\n`{user['limit']}`\n\n"
            "📱 *Aplicativos e Arquivos de Configuração:*\n\n"
            "\\- *Para iOS:*\n"
            "  \\- *Aplicativo:* [Baixe aqui](https://apps.apple.com/us/app/npv-tunnel/id1629465476)\n"
            "  \\- *Arquivos de Configuração:* [Clique aqui](https://t.me/+R72mmGw8JMdiZWEx)\n\n"
            "\\- *Para Android:*\n"
            "  \\- *Aplicativo:* [Baixe aqui](https://www.mediafire.com/file/4l22uh78g37o1yl/Poison+5g+-+DT.apk/file)\n\n"
            "🌍 *Link de Renovação:*\n"
            "[Renove aqui](https://poisonbrasil.atlasssh.com/renovar.php)\n"
            "_\\(Use este link para realizar suas renovações futuras\\)_"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2", disable_web_page_preview=True)
    else:
        await update.message.reply_text("Nenhum usuário disponível para simulação de venda.")
