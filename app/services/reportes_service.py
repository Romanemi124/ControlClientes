import calendar
from app.database.db import get_connection
from app.services.clientes_service import obtener_clientes

# =========================================================
# DEUDA Y RIESGO
# =========================================================

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

    _, cuotas_pendientes = calcular_deuda_cliente(cliente_id)

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
        GROUP BY c.id, c.anio, c.mes, c.importe_previsto
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


def formatear_detalle_deuda(detalle):
    partes = []
    for d in detalle:
        partes.append(f"{d['mes']}/{d['anio']} ({d['pendiente']}€)")
    return ", ".join(partes)


def obtener_deuda_todos_clientes():
    clientes = obtener_clientes()
    resultado = []

    for cliente in clientes:
        deuda_total, cuotas_pendientes = calcular_deuda_cliente(cliente["id"])
        estado_riesgo = obtener_estado_riesgo(cliente["id"], cliente["activo"])
        detalle = obtener_detalle_deuda(cliente["id"])

        resultado.append({
            "id": cliente["id"],
            "nombre": cliente["nombre"],
            "telefono": cliente["telefono"],
            "email": cliente["email"],
            "direccion": cliente["direccion"],
            "fecha_alta": cliente["fecha_alta"],
            "fecha_baja": cliente["fecha_baja"],
            "activo": cliente["activo"],
            "deuda_total": deuda_total,
            "cuotas_pendientes": cuotas_pendientes,
            "estado_riesgo": estado_riesgo,
            "detalle_deuda": detalle,
            "detalle_deuda_texto": formatear_detalle_deuda(detalle)
        })

    return resultado


def obtener_clientes_con_deuda():
    todos = obtener_deuda_todos_clientes()
    return [cliente for cliente in todos if cliente["deuda_total"] > 0]


def obtener_clientes_baja_con_deuda():
    todos = obtener_deuda_todos_clientes()
    return [
        cliente for cliente in todos
        if cliente["activo"] == 0 and cliente["deuda_total"] > 0
    ]


# =========================================================
# ALTAS Y BAJAS
# =========================================================

def obtener_clientes_dados_de_alta():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            telefono,
            email,
            direccion,
            fecha_alta,
            fecha_baja,
            activo,
            observaciones
        FROM clientes
        WHERE fecha_alta IS NOT NULL AND fecha_alta != ''
        ORDER BY fecha_alta, nombre
    """)

    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]


def obtener_clientes_dados_de_baja():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            telefono,
            email,
            direccion,
            fecha_alta,
            fecha_baja,
            activo,
            observaciones
        FROM clientes
        WHERE activo = 0 OR (fecha_baja IS NOT NULL AND fecha_baja != '')
        ORDER BY fecha_baja, nombre
    """)

    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]


# =========================================================
# DETALLE HISTÓRICO
# Una fila por movimiento real.
# Si una cuota no tiene pagos, también aparece.
# =========================================================

def _construir_rango_mes(anio, mes):
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_inicio = f"{anio}-{mes:02d}-01"
    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia:02d}"
    return fecha_inicio, fecha_fin


def _obtener_detalle_historico(cliente_id=None, fecha_inicio=None, fecha_fin=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            c.id AS cliente_id,
            c.nombre,
            c.telefono,
            c.email,
            c.direccion,
            c.fecha_alta,
            c.fecha_baja,
            c.activo,
            cu.id AS cuota_id,
            cu.anio,
            cu.mes,
            cu.fecha_vencimiento,
            cu.importe_previsto,
            cu.estado_cuota,
            p.id AS pago_id,
            p.fecha_pago,
            p.metodo_pago,
            p.importe_pagado,
            p.referencia,
            p.observaciones AS observaciones_pago,
            ap.importe_aplicado
        FROM clientes c
        JOIN cuotas cu ON c.id = cu.cliente_id
        LEFT JOIN aplicacion_pagos ap ON cu.id = ap.cuota_id
        LEFT JOIN pagos p ON ap.pago_id = p.id
        WHERE 1 = 1
    """

    params = []

    if cliente_id is not None:
        query += " AND c.id = ?"
        params.append(cliente_id)

    if fecha_inicio is not None and fecha_fin is not None:
        query += " AND cu.fecha_vencimiento >= ? AND cu.fecha_vencimiento <= ?"
        params.extend([fecha_inicio, fecha_fin])

    query += """
        ORDER BY
            cu.fecha_vencimiento,
            p.fecha_pago,
            c.nombre,
            cu.anio,
            cu.mes
    """

    cursor.execute(query, params)
    filas = cursor.fetchall()
    conn.close()

    # Total pagado por cuota para calcular pendiente restante real
    total_por_cuota = {}
    for fila in filas:
        cuota_id = fila["cuota_id"]
        aplicado = fila["importe_aplicado"] if fila["importe_aplicado"] is not None else 0
        total_por_cuota[cuota_id] = total_por_cuota.get(cuota_id, 0) + aplicado

    resultado = []

    for fila in filas:
        cuota_id = fila["cuota_id"]
        total_pagado_cuota = total_por_cuota.get(cuota_id, 0)
        pendiente = fila["importe_previsto"] - total_pagado_cuota

        resultado.append({
            "cliente_id": fila["cliente_id"],
            "nombre": fila["nombre"],
            "telefono": fila["telefono"],
            "email": fila["email"],
            "direccion": fila["direccion"],
            "fecha_alta": fila["fecha_alta"],
            "fecha_baja": fila["fecha_baja"],
            "activo": fila["activo"],
            "cuota_id": fila["cuota_id"],
            "anio": fila["anio"],
            "mes": fila["mes"],
            "fecha_vencimiento": fila["fecha_vencimiento"],
            "importe_previsto": fila["importe_previsto"],
            "estado_cuota": fila["estado_cuota"],
            "pago_id": fila["pago_id"],
            "fecha_pago": fila["fecha_pago"],
            "metodo_pago": fila["metodo_pago"],
            "importe_pagado": fila["importe_pagado"],
            "referencia": fila["referencia"],
            "observaciones_pago": fila["observaciones_pago"],
            "importe_aplicado": fila["importe_aplicado"],
            "pendiente": pendiente,
        })

    return resultado


# =========================================================
# HISTÓRICO DETALLADO DE UN SOLO CLIENTE
# =========================================================

def obtener_historico_detallado_cliente(cliente_id):
    return _obtener_detalle_historico(cliente_id=cliente_id)


def obtener_historico_detallado_cliente_por_mes(cliente_id, anio, mes):
    fecha_inicio, fecha_fin = _construir_rango_mes(anio, mes)
    return _obtener_detalle_historico(
        cliente_id=cliente_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


def obtener_historico_detallado_cliente_por_anio(cliente_id, anio):
    return _obtener_detalle_historico(
        cliente_id=cliente_id,
        fecha_inicio=f"{anio}-01-01",
        fecha_fin=f"{anio}-12-31"
    )


def obtener_historico_detallado_cliente_por_dia(cliente_id, fecha):
    return _obtener_detalle_historico(
        cliente_id=cliente_id,
        fecha_inicio=fecha,
        fecha_fin=fecha
    )


def obtener_historico_detallado_cliente_entre_fechas(cliente_id, fecha_inicio, fecha_fin):
    return _obtener_detalle_historico(
        cliente_id=cliente_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


# =========================================================
# HISTÓRICO DETALLADO GLOBAL
# =========================================================

def obtener_historico_detallado_por_mes(anio, mes):
    fecha_inicio, fecha_fin = _construir_rango_mes(anio, mes)
    return _obtener_detalle_historico(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


def obtener_historico_detallado_por_anio(anio):
    return _obtener_detalle_historico(
        fecha_inicio=f"{anio}-01-01",
        fecha_fin=f"{anio}-12-31"
    )


def obtener_historico_detallado_por_dia(fecha):
    return _obtener_detalle_historico(
        fecha_inicio=fecha,
        fecha_fin=fecha
    )


def obtener_historico_detallado_entre_fechas(fecha_inicio, fecha_fin):
    return _obtener_detalle_historico(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


# =========================================================
# CLIENTES CRÍTICOS
# =========================================================

def obtener_clientes_criticos(limite=5):
    todos = obtener_deuda_todos_clientes()

    # ordenar por deuda descendente
    ordenados = sorted(todos, key=lambda x: x["deuda_total"], reverse=True)

    # solo los que deben dinero
    con_deuda = [c for c in ordenados if c["deuda_total"] > 0]

    return con_deuda[:limite]



def obtener_ingresos_y_deuda_por_anio(anio):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            CAST(strftime('%m', fecha_pago) AS INTEGER) as mes,
            SUM(importe_pagado) as total
        FROM pagos
        WHERE strftime('%Y', fecha_pago) = ?
        GROUP BY mes
        ORDER BY mes
    """, (str(anio),))

    ingresos_dict = {row["mes"]: row["total"] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT
            mes,
            SUM(
                importe_previsto - COALESCE((
                    SELECT SUM(ap.importe_aplicado)
                    FROM aplicacion_pagos ap
                    WHERE ap.cuota_id = cuotas.id
                ), 0)
            ) as pendiente
        FROM cuotas
        WHERE anio = ?
        GROUP BY mes
        ORDER BY mes
    """, (anio,))

    deuda_dict = {row["mes"]: row["pendiente"] for row in cursor.fetchall()}

    conn.close()

    ingresos = []
    deuda = []

    for mes in range(1, 13):
        ingresos.append(float(ingresos_dict.get(mes, 0) or 0))
        deuda.append(float(deuda_dict.get(mes, 0) or 0))

    return ingresos, deuda



