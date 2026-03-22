from app.database.db import get_connection


def crear_cliente(nombre, telefono="", email="", direccion="", fecha_alta="", observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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


def obtener_cliente_por_id(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()

    conn.close()
    return cliente


def marcar_cliente_como_baja(cliente_id, fecha_baja):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET activo = 0,
            fecha_baja = ?
        WHERE id = ?
    """, (fecha_baja, cliente_id))

    conn.commit()
    conn.close()


def reactivar_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET activo = 1,
            fecha_baja = NULL
        WHERE id = ?
    """, (cliente_id,))

    conn.commit()
    conn.close()