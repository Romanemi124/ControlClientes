import sqlite3
import os

DB_PATH = os.path.join("data", "database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)

    # Para que las filas se devuelvan como diccionarios
    conn.row_factory = sqlite3.Row

    # Activar foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn