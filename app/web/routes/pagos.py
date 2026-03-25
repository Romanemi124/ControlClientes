from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/pagos", tags=["pagos"])
templates = Jinja2Templates(directory="app/web/templates_html")


@router.get("/", response_class=HTMLResponse)
def ver_pagos(request: Request):
    return templates.TemplateResponse(
        request,
        "pagos.html",
        {
            "page_title": "Pagos",
        }
    )