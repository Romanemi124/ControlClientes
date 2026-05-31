import calendar
from datetime import datetime

from app.database.db import get_connection


MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def obtener_cuotas_cliente(cliente_id, anio=None):
    if anio is None:
        anio = datetime.now().year

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            cliente_id,
            anio,
            mes,
            importe_previsto,
            estado_cuota,
            fecha_vencimiento,
            observaciones
        FROM cuotas
        WHERE cliente_id = ?
          AND anio = ?
        ORDER BY mes ASC
    """, (cliente_id, anio))

    filas = cursor.fetchall()
    conn.close()

    cuotas = {}

    for fila in filas:
        cuotas[fila["mes"]] = {
            "id": fila["id"],
            "cliente_id": fila["cliente_id"],
            "anio": fila["anio"],
            "mes": fila["mes"],
            "mes_nombre": MESES.get(fila["mes"], fila["mes"]),
            "importe_previsto": fila["importe_previsto"] or 0,
            "estado_cuota": fila["estado_cuota"],
            "fecha_vencimiento": fila["fecha_vencimiento"],
            "observaciones": fila["observaciones"] or "",
        }

    resultado = []

    for mes in range(1, 13):
        resultado.append(
            cuotas.get(
                mes,
                {
                    "id": "",
                    "cliente_id": cliente_id,
                    "anio": anio,
                    "mes": mes,
                    "mes_nombre": MESES[mes],
                    "importe_previsto": "",
                    "estado_cuota": "pendiente",
                    "fecha_vencimiento": "",
                    "observaciones": "",
                }
            )
        )

    return resultado


def recalcular_estado_cuota(cursor, cuota_id, importe_previsto):
    cursor.execute("""
        SELECT COALESCE(SUM(importe_aplicado), 0) AS total_pagado
        FROM aplicacion_pagos
        WHERE cuota_id = ?
    """, (cuota_id,))

    total_pagado = cursor.fetchone()["total_pagado"] or 0

    if total_pagado <= 0:
        return "pendiente"
    elif total_pagado < importe_previsto:
        return "parcial"
    else:
        return "pagada"


def guardar_cuotas_cliente(cliente_id, anio, cuotas):
    conn = get_connection()
    cursor = conn.cursor()

    for cuota in cuotas:
        mes = int(cuota["mes"])
        importe = cuota.get("importe_previsto")
        observaciones = cuota.get("observaciones", "")

        if importe in [None, ""]:
            importe = 0
        else:
            importe = float(importe)

        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_vencimiento = f"{anio}-{mes:02d}-{ultimo_dia:02d}"

        cursor.execute("""
            SELECT id
            FROM cuotas
            WHERE cliente_id = ?
              AND anio = ?
              AND mes = ?
        """, (cliente_id, anio, mes))

        existente = cursor.fetchone()

        if existente:
            cuota_id = existente["id"]
            nuevo_estado = recalcular_estado_cuota(cursor, cuota_id, importe)

            cursor.execute("""
                UPDATE cuotas
                SET importe_previsto = ?,
                    estado_cuota = ?,
                    fecha_vencimiento = ?,
                    observaciones = ?
                WHERE id = ?
            """, (
                importe,
                nuevo_estado,
                fecha_vencimiento,
                observaciones,
                cuota_id
            ))

        else:
            cursor.execute("""
                INSERT INTO cuotas (
                    cliente_id,
                    anio,
                    mes,
                    importe_previsto,
                    estado_cuota,
                    fecha_vencimiento,
                    observaciones
                )
                VALUES (?, ?, ?, ?, 'pendiente', ?, ?)
            """, (
                cliente_id,
                anio,
                mes,
                importe,
                fecha_vencimiento,
                observaciones
            ))

    conn.commit()
    conn.close()