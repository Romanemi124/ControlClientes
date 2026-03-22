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


from app.database.models import create_tables
from app.services.clientes_service import obtener_clientes
from app.services.reportes_service import calcular_deuda_cliente, obtener_estado_riesgo
from app.services.reportes_service import obtener_detalle_deuda


def main():
    create_tables()

    clientes = obtener_clientes()

    for cliente in clientes:
        deuda_total, cuotas_pendientes = calcular_deuda_cliente(cliente["id"])
        estado = obtener_estado_riesgo(cliente["id"], cliente["activo"])
        detalle = obtener_detalle_deuda(cliente["id"])

        print("Cliente:", cliente["nombre"])
        print("Deuda total:", deuda_total)
        print("Detalle deuda:")
        for d in detalle:
            print(f"Mes {d['mes']}/{d['anio']} → {d['pendiente']}€")
        print("Cuotas pendientes:", cuotas_pendientes)
        print("Estado:", estado)
        print("-" * 30)


if __name__ == "__main__":
    main()