from app.database.db import get_connection

def crear_cliente(nombre, telefono = "", email = "", direccion = "", fecha_alta = "", observaciones = ""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO clientes (nombre, telefono, email, direccion, fecha_alta, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, telefono, email, direccion, fecha_alta, observaciones))

    conn.commit()
    conn.close()

def obtener_clientes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes ORDER BY nombre ASC")
    clientes = cursor.fetchall()

    conn.close()
    return clientes