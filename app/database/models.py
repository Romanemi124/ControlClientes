from app.database.db import get_connection

def create_tables():
    conn = get_connection()

    try:

        cursor = conn.cursor()

        with open("app/database/schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()

        cursor.executescript(schema)
        conn.commit()

        print("Tablas creadas o verificadas exitosamente.")

    except Exception as e:
        print("Error al crear tablas:", e)
        
    finally:
        conn.close()