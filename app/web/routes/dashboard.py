from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.clientes_service import obtener_clientes, get_clientes_mayor_deuda
from app.services.reportes_service import (
    obtener_clientes_con_deuda,
    obtener_ingresos_y_deuda_por_anio,
)
from app.services.pagos_service import (
    obtener_ultimos_pagos,
    get_pagos_devueltos,
    get_cuotas_vencidas,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    clientes = obtener_clientes()
    clientes_deuda = obtener_clientes_con_deuda()
    ultimos_pagos = obtener_ultimos_pagos()

    total_clientes = len(clientes)
    clientes_activos = len([c for c in clientes if c["activo"] == 1])
    clientes_con_deuda = len(clientes_deuda)
    deuda_total = sum(c["deuda_total"] for c in clientes_deuda)

    clientes_mayor_deuda = get_clientes_mayor_deuda()[:5]
    pagos_devueltos = get_pagos_devueltos()[:5]
    cuotas_vencidas = get_cuotas_vencidas()[:5]

    anio_actual = datetime.now().year
    ingresos, deuda = obtener_ingresos_y_deuda_por_anio(anio_actual)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "page_title": "Dashboard",
            "total_clientes": total_clientes,
            "clientes_activos": clientes_activos,
            "clientes_deuda": clientes_con_deuda,
            "deuda_total": deuda_total,
            "ultimos_pagos": ultimos_pagos,
            "clientes_mayor_deuda": clientes_mayor_deuda,
            "pagos_devueltos": pagos_devueltos,
            "cuotas_vencidas": cuotas_vencidas,
            "anio_actual": anio_actual,
            "ingresos": ingresos,
            "deuda": deuda,
        }
    )


@router.get("/grafica/{anio}")
def datos_grafica(anio: int):
    ingresos, deuda = obtener_ingresos_y_deuda_por_anio(anio)

    return JSONResponse({
        "ingresos": ingresos,
        "deuda": deuda
    })



