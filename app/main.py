from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.models import create_tables

from app.web.routes.dashboard import router as dashboard_router
from app.web.routes.clientes import router as clientes_router
from app.web.routes.deudas import router as deudas_router
from app.web.routes.pagos import router as pagos_router
from app.web.routes.exportaciones import router as exportaciones_router


app = FastAPI(title="Zentry")


# Crear tablas si no existen
# Si la base de datos ya tiene datos, NO los borra ni los modifica
create_tables()


# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")


# Rutas
app.include_router(dashboard_router)
app.include_router(clientes_router)
app.include_router(deudas_router)
app.include_router(pagos_router)
app.include_router(exportaciones_router)