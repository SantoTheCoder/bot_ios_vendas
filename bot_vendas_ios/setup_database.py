import sqlite3

def create_affiliates_table():
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
    conn.close()

# Execute esta função uma vez para criar a tabela
create_affiliates_table()
