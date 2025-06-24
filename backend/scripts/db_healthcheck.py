import logging
from sqlalchemy import text
from core.database import engine

def check_database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return False

if __name__ == "__main__":
    if check_database_health():
        print("Banco de dados está acessível!")
    else:
        print("Banco de dados NÃO está acessível!")
