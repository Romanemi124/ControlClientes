import calendar
from datetime import date

from app.database.db import get_connection


def crear_cuota(cliente_id, anio, mes, importe):
    conn = get_connection()
    cursor = conn.cursor()

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_vencimiento = f"{anio}-{mes:02d}-{ultimo_dia:02d}"

    cursor.execute("""
        INSERT INTO cuotas (
            cliente_id,
            anio,
            mes,
            importe_previsto,
            estado_cuota,
            fecha_vencimiento
        )
        VALUES (?, ?, ?, ?, 'pendiente', ?)
    """, (cliente_id, anio, mes, importe, fecha_vencimiento))

    conn.commit()
    conn.close()


def obtener_cuotas_pendientes(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cu.id,
            cu.cliente_id,
            cu.anio,
            cu.mes,
            cu.importe_previsto,
            cu.estado_cuota,
            cu.fecha_vencimiento,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_aplicado
        FROM cuotas cu
        LEFT JOIN aplicacion_pagos ap ON cu.id = ap.cuota_id
        WHERE cu.cliente_id = ? AND cu.estado_cuota != 'pagada'
        GROUP BY
            cu.id,
            cu.cliente_id,
            cu.anio,
            cu.mes,
            cu.importe_previsto,
            cu.estado_cuota,
            cu.fecha_vencimiento
        ORDER BY cu.anio, cu.mes
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    conn.close()

    return cuotas


def _recalcular_estado_cuota(cursor, cuota_id):
    cursor.execute("""
        SELECT
            cu.importe_previsto,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_aplicado
        FROM cuotas cu
        LEFT JOIN aplicacion_pagos ap ON cu.id = ap.cuota_id
        WHERE cu.id = ?
        GROUP BY cu.id, cu.importe_previsto
    """, (cuota_id,))

    cuota = cursor.fetchone()

    if not cuota:
        return

    if cuota["total_aplicado"] >= cuota["importe_previsto"]:
        estado = "pagada"
    elif cuota["total_aplicado"] > 0:
        estado = "parcial"
    else:
        estado = "pendiente"

    cursor.execute("""
        UPDATE cuotas
        SET estado_cuota = ?
        WHERE id = ?
    """, (estado, cuota_id))


def _aplicar_pago_a_cuotas(cursor, pago_id, cliente_id, importe):
    cursor.execute("""
        SELECT
            cu.id,
            cu.importe_previsto,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_aplicado
        FROM cuotas cu
        LEFT JOIN aplicacion_pagos ap ON cu.id = ap.cuota_id
        WHERE cu.cliente_id = ?
          AND cu.estado_cuota != 'pagada'
        GROUP BY cu.id, cu.importe_previsto
        ORDER BY cu.fecha_vencimiento ASC, cu.id ASC
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    restante = importe

    for cuota in cuotas:
        if restante <= 0:
            break

        pendiente = cuota["importe_previsto"] - cuota["total_aplicado"]

        if pendiente <= 0:
            continue

        importe_a_aplicar = min(restante, pendiente)

        cursor.execute("""
            INSERT INTO aplicacion_pagos (
                pago_id,
                cuota_id,
                importe_aplicado
            )
            VALUES (?, ?, ?)
        """, (pago_id, cuota["id"], importe_a_aplicar))

        restante -= importe_a_aplicar

        _recalcular_estado_cuota(cursor, cuota["id"])


def _obtener_pago_por_id(cursor, pago_id):
    cursor.execute("""
        SELECT
            p.id,
            p.cliente_id,
            c.nombre AS cliente_nombre,
            p.fecha_pago,
            p.importe_pagado,
            p.metodo_pago,
            p.referencia,
            p.observaciones
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
    """, (pago_id,))

    fila = cursor.fetchone()

    return dict(fila) if fila else None


def registrar_pago(cliente_id, importe, metodo_pago, fecha_pago=None, referencia="", observaciones=""):
    if fecha_pago is None:
        fecha_pago = str(date.today())

    return crear_pago_simple(
        cliente_id=cliente_id,
        fecha_pago=fecha_pago,
        importe=importe,
        metodo_pago=metodo_pago,
        referencia=referencia,
        observaciones=observaciones
    )


def obtener_ultimos_pagos(limite=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.fecha_pago,
            p.importe_pagado,
            p.metodo_pago,
            c.nombre
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.fecha_pago DESC, p.id DESC
        LIMIT ?
    """, (limite,))

    pagos = cursor.fetchall()
    conn.close()

    return pagos


def get_pagos_devueltos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.nombre,
            cu.importe_previsto AS importe,
            cu.fecha_vencimiento AS fecha
        FROM cuotas cu
        JOIN clientes c ON cu.cliente_id = c.id
        WHERE cu.estado_cuota = 'devuelta'
        ORDER BY cu.fecha_vencimiento DESC
    """)

    filas = cursor.fetchall()
    conn.close()

    return [
        {
            "nombre": fila["nombre"],
            "importe": fila["importe"],
            "fecha": fila["fecha"],
        }
        for fila in filas
    ]


def get_cuotas_vencidas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.nombre,
            cu.fecha_vencimiento AS fecha,
            cu.importe_previsto AS importe,
            cu.estado_cuota
        FROM cuotas cu
        JOIN clientes c ON cu.cliente_id = c.id
        WHERE cu.fecha_vencimiento < DATE('now')
          AND cu.estado_cuota != 'pagada'
        ORDER BY cu.fecha_vencimiento ASC
    """)

    filas = cursor.fetchall()
    conn.close()

    return [
        {
            "nombre": fila["nombre"],
            "fecha": fila["fecha"],
            "importe": fila["importe"],
            "estado": fila["estado_cuota"],
        }
        for fila in filas
    ]


def obtener_pagos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.cliente_id,
            c.nombre AS cliente_nombre,
            p.fecha_pago,
            p.importe_pagado,
            p.metodo_pago,
            p.referencia,
            p.observaciones
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.id ASC
    """)

    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]


def crear_pago_simple(cliente_id, fecha_pago, importe, metodo_pago, referencia="", observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pagos (
            cliente_id,
            fecha_pago,
            importe_pagado,
            metodo_pago,
            referencia,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, fecha_pago, importe, metodo_pago, referencia, observaciones))

    pago_id = cursor.lastrowid

    _aplicar_pago_a_cuotas(cursor, pago_id, cliente_id, importe)

    pago = _obtener_pago_por_id(cursor, pago_id)

    conn.commit()
    conn.close()

    return pago


def actualizar_pago(pago_id, cliente_id, fecha_pago, importe, metodo_pago, referencia="", observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cuota_id
        FROM aplicacion_pagos
        WHERE pago_id = ?
    """, (pago_id,))

    cuotas_afectadas = [fila["cuota_id"] for fila in cursor.fetchall()]

    cursor.execute("""
        DELETE FROM aplicacion_pagos
        WHERE pago_id = ?
    """, (pago_id,))

    for cuota_id in cuotas_afectadas:
        _recalcular_estado_cuota(cursor, cuota_id)

    cursor.execute("""
        UPDATE pagos
        SET cliente_id = ?,
            fecha_pago = ?,
            importe_pagado = ?,
            metodo_pago = ?,
            referencia = ?,
            observaciones = ?
        WHERE id = ?
    """, (cliente_id, fecha_pago, importe, metodo_pago, referencia, observaciones, pago_id))

    _aplicar_pago_a_cuotas(cursor, pago_id, cliente_id, importe)

    pago = _obtener_pago_por_id(cursor, pago_id)

    conn.commit()
    conn.close()

    return pago


def eliminar_pago(pago_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cuota_id
        FROM aplicacion_pagos
        WHERE pago_id = ?
    """, (pago_id,))

    cuotas_afectadas = [fila["cuota_id"] for fila in cursor.fetchall()]

    cursor.execute("""
        DELETE FROM aplicacion_pagos
        WHERE pago_id = ?
    """, (pago_id,))

    for cuota_id in cuotas_afectadas:
        _recalcular_estado_cuota(cursor, cuota_id)

    cursor.execute("""
        DELETE FROM pagos
        WHERE id = ?
    """, (pago_id,))

    conn.commit()
    conn.close()


def buscar_pagos(cliente_nombre="", fecha_pago="", metodo_pago=""):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            p.id,
            p.cliente_id,
            c.nombre AS cliente_nombre,
            p.fecha_pago,
            p.importe_pagado,
            p.metodo_pago,
            p.referencia,
            p.observaciones
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE 1 = 1
    """

    params = []

    if cliente_nombre:
        query += " AND LOWER(c.nombre) LIKE ?"
        params.append(f"%{cliente_nombre.lower()}%")

    if fecha_pago:
        query += " AND p.fecha_pago = ?"
        params.append(fecha_pago)

    if metodo_pago:
        query += " AND p.metodo_pago = ?"
        params.append(metodo_pago)

    query += " ORDER BY p.fecha_pago DESC, p.id DESC"

    cursor.execute(query, params)
    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]