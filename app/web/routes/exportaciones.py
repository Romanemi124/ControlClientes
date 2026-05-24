from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.utils.excel_export import (
    exportar_clientes_totales_excel,
    exportar_deudas_actuales_excel,
    exportar_pagos_cliente_excel,
    exportar_historico_cliente_excel,
)

from app.services.clientes_service import obtener_clientes

router = APIRouter(prefix="/exportaciones", tags=["exportaciones"])
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def ver_exportaciones(request: Request):

    clientes = obtener_clientes()

    return templates.TemplateResponse(
        request,
        "exportaciones.html",
        {
            "request": request,
            "page_title": "Exportaciones",
            "clientes": clientes,
        }
    )


@router.get("/clientes")
def exportar_clientes():
    ruta = exportar_clientes_totales_excel()

    if not ruta:
        return JSONResponse(
            {"ok": False, "error": "No hay clientes para exportar"},
            status_code=404
        )

    return FileResponse(
        path=ruta,
        filename=ruta.split("/")[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/deudas")
def exportar_deudas():
    ruta = exportar_deudas_actuales_excel()

    if not ruta:
        return JSONResponse(
            {"ok": False, "error": "No hay deudas actuales para exportar"},
            status_code=404
        )

    return FileResponse(
        path=ruta,
        filename=ruta.split("/")[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/pagos-cliente")
def exportar_pagos_cliente(cliente_nombre: str):
    if not cliente_nombre.strip():
        return JSONResponse(
            {"ok": False, "error": "Debes indicar el nombre del cliente"},
            status_code=400
        )

    ruta = exportar_pagos_cliente_excel(cliente_nombre.strip())

    if not ruta:
        return JSONResponse(
            {"ok": False, "error": "No hay pagos para ese cliente"},
            status_code=404
        )

    return FileResponse(
        path=ruta,
        filename=ruta.split("/")[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/historico-cliente")
def exportar_historico_cliente(cliente_id: int):
    ruta = exportar_historico_cliente_excel(cliente_id)

    if not ruta:
        return JSONResponse(
            {"ok": False, "error": "No hay histórico para ese cliente"},
            status_code=404
        )

    return FileResponse(
        path=ruta,
        filename=ruta.split("/")[-1],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )