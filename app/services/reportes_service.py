from app.database.db import get_connection


def calcular_deuda_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            c.importe_previsto,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_pagado
        FROM cuotas c
        LEFT JOIN aplicacion_pagos ap ON c.id = ap.cuota_id
        WHERE c.cliente_id = ?
        GROUP BY c.id, c.importe_previsto
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    conn.close()

    deuda_total = 0
    cuotas_pendientes = 0

    for cuota in cuotas:
        pendiente = cuota["importe_previsto"] - cuota["total_pagado"]
        if pendiente > 0:
            deuda_total += pendiente
            cuotas_pendientes += 1

    return deuda_total, cuotas_pendientes


def obtener_estado_riesgo(cliente_id, activo=1):
    if activo == 0:
        return "baja"

    deuda_total, cuotas_pendientes = calcular_deuda_cliente(cliente_id)

    if cuotas_pendientes == 0:
        return "al_dia"
    elif cuotas_pendientes == 1:
        return "retraso_leve"
    elif cuotas_pendientes <= 3:
        return "en_riesgo"
    else:
        return "moroso_grave"
    
def obtener_detalle_deuda(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.anio,
            c.mes,
            c.importe_previsto,
            COALESCE(SUM(ap.importe_aplicado), 0) AS total_pagado
        FROM cuotas c
        LEFT JOIN aplicacion_pagos ap ON c.id = ap.cuota_id
        WHERE c.cliente_id = ?
        GROUP BY c.id
        ORDER BY c.anio, c.mes
    """, (cliente_id,))

    cuotas = cursor.fetchall()
    conn.close()

    detalle = []

    for cuota in cuotas:
        pendiente = cuota["importe_previsto"] - cuota["total_pagado"]
        if pendiente > 0:
            detalle.append({
                "anio": cuota["anio"],
                "mes": cuota["mes"],
                "pendiente": pendiente
            })

    return detalle