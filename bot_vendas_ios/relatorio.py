#relatorio.py
import sqlite3
import logging
from datetime import datetime
from config import ADMIN_ID

logger = logging.getLogger(__name__)

def register_sale(sale_type, amount, buyer_id, buyer_name):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO sales (sale_date, sale_type, amount, buyer_id, buyer_name)
        VALUES (?, ?, ?, ?, ?)
        ''', (sale_date, sale_type, amount, buyer_id, buyer_name))
        
        conn.commit()
        logger.info(f"Venda registrada: {sale_type}, Valor: {amount}, Comprador: {buyer_name}")
    except sqlite3.Error as e:
        logger.error(f"Erro ao registrar a venda: {e}")
    finally:
        conn.close()

async def generate_report(update, context):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Por favor, forneça uma data inicial e uma data final no formato DD/MM/AAAA.")
        return

    start_date = context.args[0]
    end_date = context.args[1]

    try:
        # Convertendo as datas fornecidas para o formato utilizado no banco de dados
        start_date_db = datetime.strptime(start_date, '%d/%m/%Y').strftime('%Y-%m-%d 00:00:00')
        end_date_db = datetime.strptime(end_date, '%d/%m/%Y').strftime('%Y-%m-%d 23:59:59')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT sale_type, COUNT(*), SUM(amount)
        FROM sales
        WHERE sale_date BETWEEN ? AND ?
        GROUP BY sale_type
        ''', (start_date_db, end_date_db))

        sales_summary = cursor.fetchall()
        conn.close()

        if not sales_summary:
            logger.info(f"Nenhuma venda encontrada entre {start_date} e {end_date}.")
            await update.message.reply_text(f"Nenhuma venda encontrada entre {start_date} e {end_date}.")
            return

        total_usuarios = 0
        total_revendas = 0
        valor_total = 0.0

        for sale in sales_summary:
            sale_type, count, amount_sum = sale
            if sale_type == 'usuario':
                total_usuarios = count
            elif sale_type == 'revenda':
                total_revendas = count
            valor_total += amount_sum

        report = (
            f"📊 *Relatório Resumido de Vendas de {start_date} a {end_date}:* 📊\n\n"
            f"🔹 *Total de Vendas de Usuários:* {total_usuarios}\n"
            f"🔹 *Total de Vendas de Revenda:* {total_revendas}\n"
            f"💰 *Valor Total Vendido:* R$ {valor_total:.2f}\n"
        )

        await update.message.reply_text(report, parse_mode="Markdown")
        logger.info(f"Relatório resumido gerado com sucesso de {start_date} a {end_date}.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao gerar o relatório: {e}")
        await update.message.reply_text("Erro ao gerar o relatório.")
