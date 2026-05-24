import os
from datetime import datetime

import pandas as pd

from app.services.clientes_service import obtener_clientes
from app.services.pagos_service import buscar_pagos
from app.services.reportes_service import (
    obtener_deuda_todos_clientes,
    obtener_historico_detallado_cliente,
)

EXPORT_DIR = "exports"


def asegurar_carpeta_exports():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def nombre_archivo(nombre_base):
    asegurar_carpeta_exports()
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(EXPORT_DIR, f"{nombre_base}_{fecha}.xlsx")


def nombre_mes(numero_mes):
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }
    return meses.get(numero_mes, str(numero_mes))


def guardar_excel(filas, ruta, hoja="Datos"):
    if not filas:
        return None

    df = pd.DataFrame(filas)

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=hoja)

        worksheet = writer.sheets[hoja]

        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            worksheet.column_dimensions[column_letter].width = max_length + 3

        worksheet.auto_filter.ref = worksheet.dimensions

    return ruta


def exportar_clientes_totales_excel():
    clientes = obtener_clientes()

    filas = []
    for c in clientes:
        filas.append({
            "ID": c["id"],
            "Nombre": c["nombre"],
            "Prefijo": c["prefijo"],
            "Teléfono": c["telefono"],
            "Email": c["email"],
            "Dirección": c["direccion"],
            "Fecha alta": c["fecha_alta"],
            "Fecha baja": c["fecha_baja"],
            "Activo": "Sí" if c["activo"] == 1 else "No",
            "Observaciones": c["observaciones"],
        })

    ruta = nombre_archivo("clientes_totales")
    return guardar_excel(filas, ruta, "Clientes")


def exportar_deudas_actuales_excel():
    deudas = obtener_deuda_todos_clientes()

    filas = []
    for d in deudas:
        if d["deuda_total"] <= 0:
            continue

        filas.append({
            "ID cliente": d["id"],
            "Nombre": d["nombre"],
            "Teléfono": d["telefono"],
            "Email": d["email"],
            "Dirección": d["direccion"],
            "Fecha alta": d["fecha_alta"],
            "Fecha baja": d["fecha_baja"],
            "Activo": "Sí" if d["activo"] == 1 else "No",
            "Deuda total": d["deuda_total"],
            "Cuotas pendientes": d["cuotas_pendientes"],
            "Estado riesgo": d["estado_riesgo"],
            "Detalle deuda": d["detalle_deuda_texto"],
        })

    ruta = nombre_archivo("deudas_actuales")
    return guardar_excel(filas, ruta, "Deudas")


def exportar_pagos_cliente_excel(cliente_nombre):
    pagos = buscar_pagos(cliente_nombre=cliente_nombre)

    filas = []
    for p in pagos:
        filas.append({
            "ID pago": p["id"],
            "ID cliente": p["cliente_id"],
            "Cliente": p["cliente_nombre"],
            "Fecha pago": p["fecha_pago"],
            "Importe pagado": p["importe_pagado"],
            "Método pago": p["metodo_pago"],
            "Referencia": p["referencia"],
            "Observaciones": p["observaciones"],
        })

    nombre_limpio = cliente_nombre.strip().replace(" ", "_").lower()
    ruta = nombre_archivo(f"pagos_cliente_{nombre_limpio}")
    return guardar_excel(filas, ruta, "Pagos cliente")


def exportar_historico_cliente_excel(cliente_id):
    historico = obtener_historico_detallado_cliente(cliente_id)

    filas = []
    for h in historico:
        filas.append({
            "ID cliente": h["cliente_id"],
            "Cliente": h["nombre"],
            "Teléfono": h["telefono"],
            "Email": h["email"],
            "Dirección": h["direccion"],
            "Fecha alta": h["fecha_alta"],
            "Fecha baja": h["fecha_baja"],
            "Activo": "Sí" if h["activo"] == 1 else "No",
            "ID cuota": h["cuota_id"],
            "Año cuota": h["anio"],
            "Mes cuota": nombre_mes(h["mes"]),
            "Fecha vencimiento": h["fecha_vencimiento"],
            "Importe previsto": h["importe_previsto"],
            "Estado cuota": h["estado_cuota"],
            "ID pago": h["pago_id"],
            "Fecha pago": h["fecha_pago"],
            "Método pago": h["metodo_pago"],
            "Importe pagado": h["importe_pagado"],
            "Referencia": h["referencia"],
            "Observaciones pago": h["observaciones_pago"],
            "Importe aplicado": h["importe_aplicado"],
            "Pendiente cuota": h["pendiente"],
        })

    ruta = nombre_archivo(f"historico_cliente_{cliente_id}")
    return guardar_excel(filas, ruta, "Histórico cliente")