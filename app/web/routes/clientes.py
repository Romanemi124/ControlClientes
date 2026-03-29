from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.clientes_service import (
    obtener_clientes,
    crear_cliente_web,
    actualizar_cliente,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    clientes = obtener_clientes()

    return templates.TemplateResponse(
        request,
        "clientes.html",
        {
            "request": request,
            "page_title": "Clientes",
            "clientes": clientes
        }
    )


@router.post("/clientes/guardar")
async def guardar_cliente(request: Request):
    data = await request.json()

    cliente_id = data.get("id")
    nombre = data.get("nombre", "").strip()
    prefijo = data.get("prefijo", "+34").strip()
    telefono = data.get("telefono", "").strip()
    email = data.get("email", "").strip()
    direccion = data.get("direccion", "").strip()
    fecha_alta = data.get("fecha_alta", "").strip()
    fecha_baja = data.get("fecha_baja", "").strip()
    activo = int(data.get("activo", 1))
    observaciones = data.get("observaciones", "").strip()

    # Obligatorios
    if not nombre or not telefono or not email or not direccion or not fecha_alta:
        return JSONResponse(
            {"ok": False, "error": "Nombre, teléfono, email, dirección y fecha de alta son obligatorios"},
            status_code=400
        )

    # Si no viene activo, por defecto activo
    if activo not in [0, 1]:
        activo = 1

    if cliente_id:
        actualizar_cliente(
            cliente_id=int(cliente_id),
            nombre=nombre,
            prefijo=prefijo,
            telefono=telefono,
            email=email,
            direccion=direccion,
            fecha_alta=fecha_alta,
            fecha_baja=fecha_baja,
            activo=activo,
            observaciones=observaciones,
        )
    else:
        cliente_id = crear_cliente_web(
            nombre=nombre,
            prefijo=prefijo,
            telefono=telefono,
            email=email,
            direccion=direccion,
            fecha_alta=fecha_alta,
            fecha_baja=fecha_baja,
            activo=activo,
            observaciones=observaciones,
        )

    clientes = obtener_clientes()
    cliente_guardado = next((c for c in clientes if c["id"] == int(cliente_id)), None)

    return JSONResponse({
        "ok": True,
        "cliente": cliente_guardado
    })


@router.post("/clientes/alta")
async def alta_cliente(request: Request):
    data = await request.json()
    cliente_id = data.get("id")

    if not cliente_id:
        return JSONResponse({"ok": False, "error": "No hay cliente seleccionado"}, status_code=400)

    actualizar_cliente(
        cliente_id=int(cliente_id),
        nombre=data.get("nombre", "").strip(),
        telefono=data.get("telefono", "").strip(),
        email=data.get("email", "").strip(),
        direccion=data.get("direccion", "").strip(),
        fecha_baja="",
        activo=1,
        observaciones=data.get("observaciones", "").strip(),
    )

    return JSONResponse({"ok": True})
