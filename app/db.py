import mysql.connector
from flask import g
from .config import Config

def get_db():
    if 'db' not in g:
        try:
            print("🆕 Creating a new Database connection")
            g.db = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
        except mysql.connector.Error as e:
            print(f"Connection failed: {e}")
            return None
    else:
        print("🔄 Reusing existing database connection")
    return g.db
    

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        print("🔒 Closing database connection")
        db.close()

