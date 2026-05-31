from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.clientes_service import obtener_clientes
from app.services.cuotas_service import (
    obtener_cuotas_cliente,
    guardar_cuotas_cliente,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/cuotas", response_class=HTMLResponse)
def cuotas_page(request: Request):
    clientes = obtener_clientes()

    return templates.TemplateResponse(
        request,
        "cuotas.html",
        {
            "request": request,
            "page_title": "Cuotas",
            "clientes": clientes,
            "anio_actual": datetime.now().year,
        }
    )


@router.post("/cuotas/cliente")
async def obtener_cuotas_cliente_route(request: Request):
    data = await request.json()

    cliente_id = data.get("cliente_id")
    anio = data.get("anio", datetime.now().year)

    if not cliente_id:
        return JSONResponse(
            {"ok": False, "error": "No hay cliente seleccionado"},
            status_code=400
        )

    cuotas = obtener_cuotas_cliente(
        cliente_id=int(cliente_id),
        anio=int(anio)
    )

    return JSONResponse({
        "ok": True,
        "cuotas": cuotas
    })


@router.post("/cuotas/guardar")
async def guardar_cuotas_route(request: Request):
    data = await request.json()

    cliente_id = data.get("cliente_id")
    anio = data.get("anio", datetime.now().year)
    cuotas = data.get("cuotas", [])

    if not cliente_id:
        return JSONResponse(
            {"ok": False, "error": "Selecciona un cliente"},
            status_code=400
        )

    guardar_cuotas_cliente(
        cliente_id=int(cliente_id),
        anio=int(anio),
        cuotas=cuotas
    )

    return JSONResponse({
        "ok": True,
        "message": "Cuotas guardadas correctamente"
    })