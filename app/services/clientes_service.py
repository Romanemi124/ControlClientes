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

    cursor.execute("SELECT * FROM clientes ORDER BY id ASC")
    rows = cursor.fetchall()

    conn.close()

    clientes = []
    for row in rows:
        clientes.append({
            "id": row["id"],
            "nombre": row["nombre"],
            "prefijo": row["prefijo"] if "prefijo" in row.keys() else "+34",
            "telefono": row["telefono"],
            "email": row["email"],
            "direccion": row["direccion"],
            "fecha_alta": row["fecha_alta"],
            "fecha_baja": row["fecha_baja"],
            "activo": row["activo"],
            "observaciones": row["observaciones"],
        })

    return clientes


def obtener_cliente_por_id(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()

    conn.close()
    return cliente


def crear_cliente_web(nombre, prefijo="+34", telefono="", email="", direccion="", fecha_alta="", fecha_baja="", activo=1, observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    if not fecha_alta:
        cursor.execute("""
            INSERT INTO clientes (nombre, prefijo, telefono, email, direccion, fecha_alta, fecha_baja, activo, observaciones)
            VALUES (?, ?, ?, ?, ?, DATE('now'), ?, ?, ?)
        """, (nombre, prefijo, telefono, email, direccion, fecha_baja or None, activo, observaciones))
    else:
        cursor.execute("""
            INSERT INTO clientes (nombre, prefijo, telefono, email, direccion, fecha_alta, fecha_baja, activo, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, prefijo, telefono, email, direccion, fecha_alta, fecha_baja or None, activo, observaciones))

    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return nuevo_id


def actualizar_cliente(cliente_id, nombre, prefijo="+34", telefono="", email="", direccion="", fecha_alta="", fecha_baja="", activo=1, observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET nombre = ?,
            prefijo = ?,
            telefono = ?,
            email = ?,
            direccion = ?,
            fecha_alta = ?,
            fecha_baja = ?,
            activo = ?,
            observaciones = ?
        WHERE id = ?
    """, (nombre, prefijo, telefono, email, direccion, fecha_alta or None, fecha_baja or None, activo, observaciones, cliente_id))

    conn.commit()
    conn.close()


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


def get_clientes_mayor_deuda():
    from app.services.reportes_service import obtener_clientes_con_deuda

    clientes_deuda = obtener_clientes_con_deuda()

    return [
        {
            "nombre": cliente["nombre"],
            "deuda": cliente["deuda_total"],
        }
        for cliente in sorted(
            clientes_deuda,
            key=lambda x: x["deuda_total"],
            reverse=True
        )
    ]


