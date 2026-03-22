import os
import pandas as pd
from app.services.reportes_service import (
    obtener_historico_detallado_cliente,
    obtener_historico_detallado_cliente_por_mes,
    obtener_historico_detallado_cliente_por_anio,
    obtener_historico_detallado_cliente_por_dia,
    obtener_historico_detallado_cliente_entre_fechas,
    obtener_historico_detallado_por_mes,
    obtener_historico_detallado_por_anio,
    obtener_historico_detallado_por_dia,
    obtener_historico_detallado_entre_fechas,
    obtener_clientes_con_deuda,
    obtener_clientes_baja_con_deuda,
    obtener_clientes_dados_de_alta,
    obtener_clientes_dados_de_baja,
)


def asegurar_carpeta_exports():
    os.makedirs("exports", exist_ok=True)


def nombre_mes(numero_mes):
    meses = {
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
    return meses.get(numero_mes, str(numero_mes))


def _exportar_detalle_excel(datos, ruta):
    asegurar_carpeta_exports()

    if not datos:
        print("No hay datos")
        return

    filas = []
    for fila in datos:
        filas.append({
            "Cliente": fila["nombre"],
            "Teléfono": fila["telefono"],
            "Email": fila["email"],
            "Dirección": fila["direccion"],
            "Fecha alta": fila["fecha_alta"],
            "Fecha baja": fila["fecha_baja"],
            "Activo": "Sí" if fila["activo"] == 1 else "No",
            "Año cuota": fila["anio"],
            "Mes cuota": nombre_mes(fila["mes"]),
            "Fecha vencimiento": fila["fecha_vencimiento"],
            "Importe previsto": fila["importe_previsto"],
            "Fecha pago": fila["fecha_pago"],
            "Método pago": fila["metodo_pago"],
            "Importe pago": fila["importe_pagado"],
            "Importe aplicado": fila["importe_aplicado"],
            "Referencia": fila["referencia"],
            "Observaciones pago": fila["observaciones_pago"],
            "Pendiente cuota": fila["pendiente"],
            "Estado cuota": fila["estado_cuota"],
        })

    df = pd.DataFrame(filas)
    df.to_excel(ruta, index=False)
    print(f"Excel generado en: {ruta}")


# =========================================================
# 1. HISTÓRICO DETALLADO DE UN SOLO CLIENTE
# =========================================================

def exportar_historico_detallado_cliente_excel(cliente_id, ruta=None):
    datos = obtener_historico_detallado_cliente(cliente_id)

    if not datos:
        print("No hay datos para este cliente")
        return

    if ruta is None:
        nombre_cliente = datos[0]["nombre"].replace(" ", "_")
        ruta = f"exports/historico_detallado_{nombre_cliente}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_detallado_cliente_por_mes_excel(cliente_id, anio, mes, ruta=None):
    datos = obtener_historico_detallado_cliente_por_mes(cliente_id, anio, mes)

    if not datos:
        print("No hay datos para este cliente en ese mes")
        return

    if ruta is None:
        nombre_cliente = datos[0]["nombre"].replace(" ", "_")
        ruta = f"exports/historico_detallado_{nombre_cliente}_{anio}_{mes:02d}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_detallado_cliente_por_anio_excel(cliente_id, anio, ruta=None):
    datos = obtener_historico_detallado_cliente_por_anio(cliente_id, anio)

    if not datos:
        print("No hay datos para este cliente en ese año")
        return

    if ruta is None:
        nombre_cliente = datos[0]["nombre"].replace(" ", "_")
        ruta = f"exports/historico_detallado_{nombre_cliente}_{anio}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_detallado_cliente_por_dia_excel(cliente_id, fecha, ruta=None):
    datos = obtener_historico_detallado_cliente_por_dia(cliente_id, fecha)

    if not datos:
        print("No hay datos para este cliente en ese día")
        return

    if ruta is None:
        nombre_cliente = datos[0]["nombre"].replace(" ", "_")
        ruta = f"exports/historico_detallado_{nombre_cliente}_{fecha}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_detallado_cliente_entre_fechas_excel(cliente_id, fecha_inicio, fecha_fin, ruta=None):
    datos = obtener_historico_detallado_cliente_entre_fechas(cliente_id, fecha_inicio, fecha_fin)

    if not datos:
        print("No hay datos para este cliente en ese rango")
        return

    if ruta is None:
        nombre_cliente = datos[0]["nombre"].replace(" ", "_")
        ruta = f"exports/historico_detallado_{nombre_cliente}_{fecha_inicio}_a_{fecha_fin}.xlsx"

    _exportar_detalle_excel(datos, ruta)


# =========================================================
# 2. HISTÓRICO DETALLADO GLOBAL
# =========================================================

def exportar_historico_mes_excel(anio, mes, ruta=None):
    datos = obtener_historico_detallado_por_mes(anio, mes)

    if ruta is None:
        ruta = f"exports/historico_detallado_{anio}_{mes:02d}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_anio_excel(anio, ruta=None):
    datos = obtener_historico_detallado_por_anio(anio)

    if ruta is None:
        ruta = f"exports/historico_detallado_{anio}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_dia_excel(fecha, ruta=None):
    datos = obtener_historico_detallado_por_dia(fecha)

    if ruta is None:
        ruta = f"exports/historico_detallado_{fecha}.xlsx"

    _exportar_detalle_excel(datos, ruta)


def exportar_historico_entre_fechas_excel(fecha_inicio, fecha_fin, ruta=None):
    datos = obtener_historico_detallado_entre_fechas(fecha_inicio, fecha_fin)

    if ruta is None:
        ruta = f"exports/historico_detallado_{fecha_inicio}_a_{fecha_fin}.xlsx"

    _exportar_detalle_excel(datos, ruta)


# =========================================================
# 6. CLIENTES CON DEUDA
# =========================================================

def exportar_clientes_con_deuda_excel(ruta="exports/clientes_con_deuda.xlsx"):
    asegurar_carpeta_exports()

    datos = obtener_clientes_con_deuda()

    if not datos:
        print("No hay clientes con deuda")
        return

    filas = []
    for cliente in datos:
        filas.append({
            "Nombre": cliente["nombre"],
            "Teléfono": cliente["telefono"],
            "Email": cliente["email"],
            "Dirección": cliente["direccion"],
            "Fecha alta": cliente["fecha_alta"],
            "Fecha baja": cliente["fecha_baja"],
            "Activo": "Sí" if cliente["activo"] == 1 else "No",
            "Deuda total": cliente["deuda_total"],
            "Cuotas pendientes": cliente["cuotas_pendientes"],
            "Estado riesgo": cliente["estado_riesgo"],
            "Detalle deuda": cliente["detalle_deuda_texto"],
        })

    df = pd.DataFrame(filas)
    df.to_excel(ruta, index=False)
    print(f"Excel generado en: {ruta}")


# =========================================================
# 7. CLIENTES DE BAJA CON DEUDA
# =========================================================

def exportar_clientes_baja_con_deuda_excel(ruta="exports/clientes_baja_con_deuda.xlsx"):
    asegurar_carpeta_exports()

    datos = obtener_clientes_baja_con_deuda()

    if not datos:
        print("No hay clientes de baja con deuda")
        return

    filas = []
    for cliente in datos:
        filas.append({
            "Nombre": cliente["nombre"],
            "Teléfono": cliente["telefono"],
            "Email": cliente["email"],
            "Dirección": cliente["direccion"],
            "Fecha alta": cliente["fecha_alta"],
            "Fecha baja": cliente["fecha_baja"],
            "Activo": "Sí" if cliente["activo"] == 1 else "No",
            "Deuda total": cliente["deuda_total"],
            "Cuotas pendientes": cliente["cuotas_pendientes"],
            "Estado riesgo": cliente["estado_riesgo"],
            "Detalle deuda": cliente["detalle_deuda_texto"],
        })

    df = pd.DataFrame(filas)
    df.to_excel(ruta, index=False)
    print(f"Excel generado en: {ruta}")


# =========================================================
# 8. TODOS LOS CLIENTES DADOS DE ALTA
# =========================================================

def exportar_clientes_dados_de_alta_excel(ruta="exports/clientes_dados_de_alta.xlsx"):
    asegurar_carpeta_exports()

    datos = obtener_clientes_dados_de_alta()

    if not datos:
        print("No hay clientes dados de alta")
        return

    df = pd.DataFrame(datos)
    df.to_excel(ruta, index=False)
    print(f"Excel generado en: {ruta}")


# =========================================================
# 9. TODOS LOS CLIENTES DADOS DE BAJA
# =========================================================

def exportar_clientes_dados_de_baja_excel(ruta="exports/clientes_dados_de_baja.xlsx"):
    asegurar_carpeta_exports()

    datos = obtener_clientes_dados_de_baja()

    if not datos:
        print("No hay clientes dados de baja")
        return

    df = pd.DataFrame(datos)
    df.to_excel(ruta, index=False)
    print(f"Excel generado en: {ruta}")