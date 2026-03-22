import calendar
from app.database.db import get_connection


def crear_cuota(cliente_id, anio, mes, importe):
    conn = get_connection()
    cursor = conn.cursor()

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_vencimiento = f"{anio}-{mes:02d}-{ultimo_dia:02d}"

    cursor.execute("""
        INSERT INTO cuotas (cliente_id, anio, mes, importe_previsto, estado_cuota, fecha_vencimiento)
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
        GROUP BY cu.id, cu.cliente_id, cu.anio, cu.mes, cu.importe_previsto, cu.estado_cuota, cu.fecha_vencimiento
        ORDER BY cu.anio, cu.mes
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    conn.close()
    return cuotas


def registrar_pago(cliente_id, importe, metodo_pago, fecha_pago=None, referencia="", observaciones=""):
    conn = get_connection()
    cursor = conn.cursor()

    if fecha_pago is None:
        fecha_pago_sql = "DATE('now')"
        params_pago = (cliente_id, importe, metodo_pago, referencia, observaciones)
        cursor.execute(f"""
            INSERT INTO pagos (cliente_id, fecha_pago, importe_pagado, metodo_pago, referencia, observaciones)
            VALUES (?, {fecha_pago_sql}, ?, ?, ?, ?)
        """, params_pago)
    else:
        cursor.execute("""
            INSERT INTO pagos (cliente_id, fecha_pago, importe_pagado, metodo_pago, referencia, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cliente_id, fecha_pago, importe, metodo_pago, referencia, observaciones))

    pago_id = cursor.lastrowid

    cursor.execute("""
        SELECT
            cu.id,
            cu.importe_previsto,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_aplicado
        FROM cuotas cu
        LEFT JOIN aplicacion_pagos ap ON cu.id = ap.cuota_id
        WHERE cu.cliente_id = ? AND cu.estado_cuota != 'pagada'
        GROUP BY cu.id, cu.importe_previsto
        ORDER BY cu.id
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    restante = importe

    for cuota in cuotas:
        if restante <= 0:
            break

        deuda_restante = cuota["importe_previsto"] - cuota["total_aplicado"]

        if deuda_restante <= 0:
            continue

        if restante >= deuda_restante:
            importe_a_aplicar = deuda_restante
        else:
            importe_a_aplicar = restante

        cursor.execute("""
            INSERT INTO aplicacion_pagos (pago_id, cuota_id, importe_aplicado)
            VALUES (?, ?, ?)
        """, (pago_id, cuota["id"], importe_a_aplicar))

        restante -= importe_a_aplicar

        nuevo_total_aplicado = cuota["total_aplicado"] + importe_a_aplicar

        if nuevo_total_aplicado >= cuota["importe_previsto"]:
            nuevo_estado = "pagada"
        else:
            nuevo_estado = "parcial"

        cursor.execute("""
            UPDATE cuotas
            SET estado_cuota = ?
            WHERE id = ?
        """, (nuevo_estado, cuota["id"]))

    conn.commit()
    conn.close()