from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.clientes_service import obtener_clientes

router = APIRouter(prefix="/clientes", tags=["clientes"])
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def listar_clientes(request: Request):
    clientes = obtener_clientes()

    return templates.TemplateResponse(
        request,
        "clientes.html",
        {
            "page_title": "Clientes",
            "clientes": clientes,
        }
    )