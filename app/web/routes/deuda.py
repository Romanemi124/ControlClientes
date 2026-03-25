from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.reportes_service import obtener_clientes_con_deuda

router = APIRouter(prefix="/deuda", tags=["deuda"])
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def ver_deuda(request: Request):
    clientes_con_deuda = obtener_clientes_con_deuda()

    return templates.TemplateResponse(
        request,
        "deuda.html",
        {
            "page_title": "Deuda",
            "clientes_con_deuda": clientes_con_deuda,
        }
    )