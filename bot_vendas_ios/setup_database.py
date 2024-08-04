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

def create_users_table():
    try:
        conn = sqlite3.connect('database.db')  # Substitua pelo caminho correto para o seu banco de dados
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            username TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Tabela 'users' criada ou já existente no banco de dados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar a tabela 'users': {e}")
    finally:
        conn.close()

def create_sales_table():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT NOT NULL,
            sale_type TEXT NOT NULL, -- 'user' ou 'reseller'
            amount REAL NOT NULL,
            buyer_id INTEGER NOT NULL,
            buyer_name TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        logger.info("Tabela 'sales' criada ou já existente no banco de dados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar a tabela 'sales': {e}")
    finally:
        conn.close()

# Execute as funções uma vez para criar as tabelas
create_affiliates_table()
create_users_table()
create_sales_table()
