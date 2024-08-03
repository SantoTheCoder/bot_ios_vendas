import sqlite3
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('database.db')  # Certifique-se de usar o caminho correto para o seu banco de dados
        conn.row_factory = sqlite3.Row
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None
