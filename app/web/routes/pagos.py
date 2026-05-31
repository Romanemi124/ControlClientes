from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.clientes_service import obtener_clientes
from app.services.pagos_service import (
    crear_pago_simple,
    actualizar_pago,
    eliminar_pago,
    buscar_pagos,
    obtener_resumen_cuotas_cliente,
    obtener_pagos_cliente,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/pagos", response_class=HTMLResponse)
def pagos_page(request: Request):
    clientes = obtener_clientes()

    return templates.TemplateResponse(
        request,
        "pagos.html",
        {
            "request": request,
            "page_title": "Pagos",
            "clientes": clientes,
            "pagos": [],  # tabla vacía al inicio
        }
    )


@router.post("/pagos/guardar")
async def guardar_pago(request: Request):
    data = await request.json()

    pago_id = data.get("id")
    cliente_id = data.get("cliente_id")
    fecha_pago = data.get("fecha_pago", "").strip()
    importe = data.get("importe")
    metodo_pago = data.get("metodo_pago", "").strip()
    referencia = data.get("referencia", "").strip()
    observaciones = data.get("observaciones", "").strip()

    if not cliente_id or not fecha_pago or importe in [None, ""] or not metodo_pago:
        return JSONResponse(
            {"ok": False, "error": "Cliente, fecha, importe y método son obligatorios"},
            status_code=400
        )

    try:
        importe = float(importe)
    except (TypeError, ValueError):
        return JSONResponse(
            {"ok": False, "error": "El importe no es válido"},
            status_code=400
        )

    if importe <= 0:
        return JSONResponse(
            {"ok": False, "error": "El importe debe ser mayor que 0"},
            status_code=400
        )

    if pago_id:
        pago = actualizar_pago(
            pago_id=int(pago_id),
            cliente_id=int(cliente_id),
            fecha_pago=fecha_pago,
            importe=importe,
            metodo_pago=metodo_pago,
            referencia=referencia,
            observaciones=observaciones,
        )
    else:
        pago = crear_pago_simple(
            cliente_id=int(cliente_id),
            fecha_pago=fecha_pago,
            importe=importe,
            metodo_pago=metodo_pago,
            referencia=referencia,
            observaciones=observaciones,
        )

    return JSONResponse({"ok": True, "pago": pago})


@router.post("/pagos/eliminar")
async def eliminar_pago_route(request: Request):
    data = await request.json()
    pago_id = data.get("id")

    if not pago_id:
        return JSONResponse(
            {"ok": False, "error": "No hay pago seleccionado"},
            status_code=400
        )

    eliminar_pago(int(pago_id))
    return JSONResponse({"ok": True})


@router.post("/pagos/buscar")
async def buscar_pagos_route(request: Request):
    data = await request.json()

    cliente_nombre = data.get("cliente_nombre", "").strip()
    fecha_pago = data.get("fecha_pago", "").strip()
    metodo_pago = data.get("metodo_pago", "").strip()

    pagos = buscar_pagos(
        cliente_nombre=cliente_nombre,
        fecha_pago=fecha_pago,
        metodo_pago=metodo_pago,
    )

    return JSONResponse({"ok": True, "pagos": pagos})

from datetime import datetime

@router.post("/pagos/resumen-cliente")
async def resumen_cliente(request: Request):
    data = await request.json()

    cliente_id = data.get("cliente_id")
    anio = data.get("anio", datetime.now().year)

    if not cliente_id:
        return JSONResponse(
            {"ok": False, "error": "No hay cliente seleccionado"},
            status_code=400
        )

    resumen = obtener_resumen_cuotas_cliente(
        int(cliente_id),
        int(anio)
    )

    pagos = obtener_pagos_cliente(
        int(cliente_id)
    )

    return JSONResponse({
        "ok": True,
        "resumen": resumen,
        "pagos": pagos
    })