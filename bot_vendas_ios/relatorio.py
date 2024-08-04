#relatorio.py
import sqlite3
import logging
from datetime import datetime

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
    if len(context.args) < 2:
        await update.message.reply_text("Por favor, forneça uma data inicial e uma data final no formato YYYY-MM-DD.")
        return

    start_date = context.args[0]
    end_date = context.args[1]

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT sale_date, sale_type, amount, buyer_name
        FROM sales
        WHERE sale_date BETWEEN ? AND ?
        ORDER BY sale_date
        ''', (start_date, end_date))

        sales = cursor.fetchall()
        conn.close()

        if not sales:
            await update.message.reply_text(f"Nenhuma venda encontrada entre {start_date} e {end_date}.")
            return

        report = f"📊 *Relatório de Vendas de {start_date} a {end_date}:* 📊\n\n"
        total_amount = 0

        for sale in sales:
            sale_date, sale_type, amount, buyer_name = sale
            report += f"Data: {sale_date}\nTipo: {sale_type}\nValor: R$ {amount:.2f}\nComprador: {buyer_name}\n\n"
            total_amount += amount

        report += f"🔹 *Total Vendido:* R$ {total_amount:.2f}\n"

        await update.message.reply_text(report, parse_mode="Markdown")
    except sqlite3.Error as e:
        logger.error(f"Erro ao gerar o relatório: {e}")
        await update.message.reply_text("Erro ao gerar o relatório.")
