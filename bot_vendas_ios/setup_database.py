import sqlite3
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_affiliates_table():
    try:
        conn = sqlite3.connect('database.db')  # Certifique-se de usar o caminho correto para o seu banco de dados
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            affiliate_id INTEGER NOT NULL,
            referred_user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        logger.info("Tabela 'affiliates' criada ou já existente no banco de dados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar a tabela 'affiliates': {e}")
    finally:
        conn.close()

# Execute esta função uma vez para criar a tabela
create_affiliates_table()
