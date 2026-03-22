from app.database.db import get_connection

def crear_cuota(cliente_id, anio, mes, importe):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cuotas (cliente_id, anio, mes, importe_previsto, estado_cuota)
        VALUES (?, ?, ?, ?, 'pendiente')
    """, (cliente_id, anio, mes, importe))

    conn.commit()
    conn.close()

def obtener_cuotas_pendientes(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM cuotas
        WHERE cliente_id = ? AND estado_cuota != 'pagada'
        ORDER BY anio, mes
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    conn.close()
    return cuotas


def registrar_pago(cliente_id, importe, metodo_pago):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Crear el pago
    cursor.execute("""
        INSERT INTO pagos (cliente_id, fecha_pago, importe_pagado, metodo_pago)
        VALUES (?, DATE('now'), ?, ?)
    """, (cliente_id, importe, metodo_pago))

    pago_id = cursor.lastrowid

    # 2. Obtener cuotas pendientes
    cursor.execute("""
        SELECT * FROM cuotas
        WHERE cliente_id = ? AND estado_cuota != 'pagada'
        ORDER BY anio, mes
    """, (cliente_id,))

    cuotas = cursor.fetchall()

    restante = importe

    # 3. Aplicar pago a cuotas (de más antigua a más nueva)
    for cuota in cuotas:
        if restante <= 0:
            break

        deuda = cuota["importe_previsto"]

        if restante >= deuda:
            # pagar cuota completa
            cursor.execute("""
                INSERT INTO aplicacion_pagos (pago_id, cuota_id, importe_aplicado)
                VALUES (?, ?, ?)
            """, (pago_id, cuota["id"], deuda))

            cursor.execute("""
                UPDATE cuotas SET estado_cuota = 'pagada'
                WHERE id = ?
            """, (cuota["id"],))

            restante -= deuda

        else:
            # pago parcial
            cursor.execute("""
                INSERT INTO aplicacion_pagos (pago_id, cuota_id, importe_aplicado)
                VALUES (?, ?, ?)
            """, (pago_id, cuota["id"], restante))

            cursor.execute("""
                UPDATE cuotas SET estado_cuota = 'parcial'
                WHERE id = ?
            """, (cuota["id"],))

            restante = 0

    conn.commit()
    conn.close()