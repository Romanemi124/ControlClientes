from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.reportes_service import (
    obtener_deuda_todos_clientes,
    obtener_clientes_con_deuda,
    obtener_clientes_baja_con_deuda,
    obtener_detalle_deuda,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates_html")

@router.get("/deudas", response_class=HTMLResponse)
def deudas_page(request: Request):
    clientes_con_deuda = obtener_clientes_con_deuda()
    clientes_baja_con_deuda = obtener_clientes_baja_con_deuda()
    todos = obtener_deuda_todos_clientes()

    resumen = {
        "clientes_con_deuda": len(clientes_con_deuda),
        "deuda_total": sum(c["deuda_total"] for c in clientes_con_deuda),
        "clientes_baja_con_deuda": len(clientes_baja_con_deuda),
        "cuotas_pendientes": sum(c["cuotas_pendientes"] for c in todos),
    }

    return templates.TemplateResponse(
        request,
        "deudas.html",
        {
            "request": request,
            "page_title": "Deudas",
            "resumen": resumen,
            "deudas": [],
        }
    )


@router.post("/deudas/buscar")
async def buscar_deudas(request: Request):
    data = await request.json()

    nombre = data.get("nombre", "").strip().lower()
    estado = data.get("estado", "").strip()
    riesgo = data.get("riesgo", "").strip()

    todos = obtener_deuda_todos_clientes()
    resultado = []

    for cliente in todos:
        if nombre and nombre not in cliente["nombre"].lower():
            continue

        if estado == "con_deuda" and cliente["deuda_total"] <= 0:
            continue

        if estado == "baja" and not (cliente["activo"] == 0 and cliente["deuda_total"] > 0):
            continue

        if riesgo and cliente["estado_riesgo"] != riesgo:
            continue

        resultado.append(cliente)

    return JSONResponse({"ok": True, "deudas": resultado})


@router.post("/deudas/detalle")
async def detalle_cliente(request: Request):
    data = await request.json()
    cliente_id = data.get("cliente_id")

    if not cliente_id:
        return JSONResponse(
            {"ok": False, "error": "No hay cliente seleccionado"},
            status_code=400
        )

    cliente_id = int(cliente_id)

    todos = obtener_deuda_todos_clientes()
    cliente = next((c for c in todos if c["id"] == cliente_id), None)

    if cliente is None:
        return JSONResponse(
            {"ok": False, "error": "Cliente no encontrado"},
            status_code=404
        )

    detalle = obtener_detalle_deuda(cliente_id)

    return JSONResponse({
        "ok": True,
        "detalle": detalle,
        "cliente": cliente
    })
