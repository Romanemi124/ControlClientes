from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.clientes_service import (
    obtener_clientes,
    crear_cliente_web,
    actualizar_cliente,
)

import re


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
    try:
        activo = int(data.get("activo", 1))
    except (ValueError, TypeError):
        activo = 1 
    observaciones = data.get("observaciones", "").strip()

    # =====================================================
    # VALIDACIONES OBLIGATORIAS
    # =====================================================

    errores = []

    if not nombre:
        errores.append("nombre")

    if not telefono:
        errores.append("teléfono")

    if not fecha_alta:
        errores.append("fecha de alta")

    if errores:
        return JSONResponse(
            {
                "ok": False,
                "error": f"Faltan campos obligatorios: {', '.join(errores)}"
            },
            status_code=400
        )

    # =====================================================
    # VALIDACIÓN EMAIL
    # =====================================================

    patron_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if email and not re.match(patron_email, email):
        return JSONResponse(
            {
                "ok": False,
                "error": "El email no es válido"
            },
            status_code=400
        )

    # =====================================================
    # VALIDACIÓN TELÉFONO
    # =====================================================

    telefono_limpio = telefono.replace(" ", "").replace("-", "")

    if not telefono_limpio.isdigit():
        return JSONResponse(
            {
                "ok": False,
                "error": "El teléfono solo puede contener números"
            },
            status_code=400
        )

    if len(telefono_limpio) < 6 or len(telefono_limpio) > 15:
        return JSONResponse(
            {
                "ok": False,
                "error": "El teléfono no tiene un formato válido"
            },
            status_code=400
        )

    # =====================================================
    # NORMALIZAR ACTIVO
    # =====================================================

    if activo not in [0, 1]:
        activo = 1

    # Si vuelve a activo → limpiar fecha baja
    if activo == 1:
        fecha_baja = ""

    # =====================================================
    # GUARDAR
    # =====================================================

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

    cliente_guardado = next(
        (c for c in clientes if c["id"] == int(cliente_id)),
        None
    )

    return JSONResponse({
        "ok": True,
        "cliente": cliente_guardado
    })