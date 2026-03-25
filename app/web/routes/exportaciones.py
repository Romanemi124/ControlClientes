from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/exportaciones", tags=["exportaciones"])
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def ver_exportaciones(request: Request):
    return templates.TemplateResponse(
        request,
        "exportaciones.html",
        {
            "page_title": "Exportaciones",
        }
    )