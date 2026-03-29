from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.db import get_connection
from app.database.models import create_tables

from app.services.clientes_service import crear_cliente_web, obtener_clientes, actualizar_cliente
from app.services.pagos_service import crear_cuota, registrar_pago

from app.web.routes.dashboard import router as dashboard_router
from app.web.routes.clientes import router as clientes_router
from app.web.routes.deuda import router as deuda_router
from app.web.routes.pagos import router as pagos_router
from app.web.routes.exportaciones import router as exportaciones_router


app = FastAPI(title="ControlClientes")


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM clientes")
    total_clientes = cursor.fetchone()["total"]
    conn.close()

    if total_clientes > 0:
        print("La base de datos ya tiene datos. No se insertan datos de prueba.")
        return

    print("Insertando datos de prueba...")

    clientes_demo = [
        {
            "nombre": "Ana Pérez",
            "prefijo": "+34",
            "telefono": "612345678",
            "email": "ana.perez@gmail.com",
            "direccion": "Calle Mayor 1, Madrid",
            "fecha_alta": "2023-01-10",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente habitual"
        },
        {
            "nombre": "Luis García",
            "prefijo": "+34",
            "telefono": "678912345",
            "email": "luis.garcia@gmail.com",
            "direccion": "Avenida Sol 23, Valencia",
            "fecha_alta": "2023-02-15",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Pago puntual"
        },
        {
            "nombre": "María López",
            "prefijo": "+34",
            "telefono": "699123456",
            "email": "maria.lopez@gmail.com",
            "direccion": "Calle Luna 5, Sevilla",
            "fecha_alta": "2022-11-20",
            "fecha_baja": "2024-01-01",
            "activo": 0,
            "observaciones": "Cliente inactivo"
        },
        {
            "nombre": "Carlos Ruiz",
            "prefijo": "+33",
            "telefono": "123456789",
            "email": "carlos.ruiz@gmail.com",
            "direccion": "Rue Paris 10, París",
            "fecha_alta": "2021-07-12",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente internacional"
        },
        {
            "nombre": "Laura Fernández",
            "prefijo": "+34",
            "telefono": "634567890",
            "email": "laura.fernandez@gmail.com",
            "direccion": "Calle Norte 12, Bilbao",
            "fecha_alta": "2024-03-01",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Nueva alta"
        },
        {
            "nombre": "David Martín",
            "prefijo": "+49",
            "telefono": "1234567890",
            "email": "david.martin@gmail.com",
            "direccion": "Berlin Strasse 45, Berlín",
            "fecha_alta": "2022-05-18",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente extranjero"
        },
        {
            "nombre": "Elena Sánchez",
            "prefijo": "+34",
            "telefono": "622334455",
            "email": "elena.sanchez@gmail.com",
            "direccion": "Gran Vía 100, Madrid",
            "fecha_alta": "2023-09-09",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente frecuente"
        },
        {
            "nombre": "Javier Gómez",
            "prefijo": "+34",
            "telefono": "611223344",
            "email": "javier.gomez@gmail.com",
            "direccion": "Calle Sur 77, Málaga",
            "fecha_alta": "2021-12-25",
            "fecha_baja": "2023-06-01",
            "activo": 0,
            "observaciones": "Baja por impago"
        },
        {
            "nombre": "Paula Díaz",
            "prefijo": "+34",
            "telefono": "688776655",
            "email": "paula.diaz@gmail.com",
            "direccion": "Av. Andalucía 9, Granada",
            "fecha_alta": "2024-01-11",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente reciente"
        },
        {
            "nombre": "Miguel Torres",
            "prefijo": "+34",
            "telefono": "677889900",
            "email": "miguel.torres@gmail.com",
            "direccion": "Calle Este 3, Zaragoza",
            "fecha_alta": "2022-03-30",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Sin incidencias"
        },
        {
            "nombre": "Sara Romero",
            "prefijo": "+34",
            "telefono": "655443322",
            "email": "sara.romero@gmail.com",
            "direccion": "Calle Oeste 14, Vigo",
            "fecha_alta": "2023-06-05",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente activo"
        },
        {
            "nombre": "Daniel Navarro",
            "prefijo": "+34",
            "telefono": "699888777",
            "email": "daniel.navarro@gmail.com",
            "direccion": "Av. Castilla 55, Valladolid",
            "fecha_alta": "2021-08-08",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente VIP"
        },
        {
            "nombre": "Lucía Castro",
            "prefijo": "+34",
            "telefono": "612121212",
            "email": "lucia.castro@gmail.com",
            "direccion": "Calle Real 2, Toledo",
            "fecha_alta": "2023-04-14",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente normal"
        },
        {
            "nombre": "Alejandro Vega",
            "prefijo": "+39",
            "telefono": "987654321",
            "email": "alejandro.vega@gmail.com",
            "direccion": "Via Roma 8, Roma",
            "fecha_alta": "2022-10-01",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente extranjero"
        },
        {
            "nombre": "Marta Ortiz",
            "prefijo": "+34",
            "telefono": "633221100",
            "email": "marta.ortiz@gmail.com",
            "direccion": "Calle Jardín 6, Murcia",
            "fecha_alta": "2023-07-19",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente recurrente"
        },
        {
            "nombre": "Raúl Jiménez",
            "prefijo": "+34",
            "telefono": "666555444",
            "email": "raul.jimenez@gmail.com",
            "direccion": "Calle Central 11, Alicante",
            "fecha_alta": "2024-02-20",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Nuevo cliente"
        },
        {
            "nombre": "Carmen Moreno",
            "prefijo": "+34",
            "telefono": "644332211",
            "email": "carmen.moreno@gmail.com",
            "direccion": "Calle Alta 90, Córdoba",
            "fecha_alta": "2021-11-11",
            "fecha_baja": "2022-12-12",
            "activo": 0,
            "observaciones": "Baja voluntaria"
        },
        {
            "nombre": "Alberto Herrera",
            "prefijo": "+34",
            "telefono": "677112233",
            "email": "alberto.herrera@gmail.com",
            "direccion": "Calle Baja 22, Salamanca",
            "fecha_alta": "2022-06-06",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente activo"
        },
        {
            "nombre": "Patricia Molina",
            "prefijo": "+34",
            "telefono": "688334455",
            "email": "patricia.molina@gmail.com",
            "direccion": "Av. Mar 15, Cádiz",
            "fecha_alta": "2023-08-22",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Cliente fiel"
        },
        {
            "nombre": "Sergio Cano",
            "prefijo": "+34",
            "telefono": "699556677",
            "email": "sergio.cano@gmail.com",
            "direccion": "Calle Río 18, León",
            "fecha_alta": "2024-03-10",
            "fecha_baja": "",
            "activo": 1,
            "observaciones": "Alta reciente"
        }
    ]

    # 1. Crear clientes
    for c in clientes_demo:
        crear_cliente_web(
            nombre=c["nombre"],
            prefijo=c["prefijo"],
            telefono=c["telefono"],
            email=c["email"],
            direccion=c["direccion"],
            fecha_alta=c["fecha_alta"],
            fecha_baja=c["fecha_baja"],
            activo=c["activo"],
            observaciones=c["observaciones"],
        )

    clientes = obtener_clientes()

    # 2. Ajustar inactivos por si quieres asegurar estado y fecha_baja
    for c in clientes_demo:
        if c["activo"] == 0:
            cliente_real = next((x for x in clientes if x["email"] == c["email"]), None)
            if cliente_real:
                actualizar_cliente(
                    cliente_id=cliente_real["id"],
                    nombre=cliente_real["nombre"],
                    prefijo=cliente_real["prefijo"],
                    telefono=cliente_real["telefono"],
                    email=cliente_real["email"],
                    direccion=cliente_real["direccion"],
                    fecha_alta=cliente_real["fecha_alta"],
                    fecha_baja=c["fecha_baja"],
                    activo=0,
                    observaciones=cliente_real["observaciones"],
                )

    clientes = obtener_clientes()

    # 3. Crear cuotas (varias por cliente, con años y meses distintos)
    for cliente in clientes:
        cid = cliente["id"]

        crear_cuota(cid, 2024, 1, 50)
        crear_cuota(cid, 2024, 2, 50)
        crear_cuota(cid, 2024, 3, 50)
        crear_cuota(cid, 2025, 1, 55)
        crear_cuota(cid, 2025, 2, 55)
        crear_cuota(cid, 2025, 3, 55)
        crear_cuota(cid, 2026, 1, 60)
        crear_cuota(cid, 2026, 2, 60)
        crear_cuota(cid, 2026, 3, 60)

    # 4. Registrar pagos (esto rellena pagos y aplicacion_pagos)
    # Algunos pagan todo, otros parcial, otros nada
    for cliente in clientes:
        cid = cliente["id"]

        if cid % 4 == 1:
            registrar_pago(cid, 100, "transferencia", fecha_pago="2024-01-20", referencia="PAGO-001", observaciones="Pago parcial")
            registrar_pago(cid, 120, "efectivo", fecha_pago="2025-02-15", referencia="PAGO-002", observaciones="Pago adicional")
            registrar_pago(cid, 180, "transferencia", fecha_pago="2026-03-12", referencia="PAGO-003", observaciones="Pago completo")
        elif cid % 4 == 2:
            registrar_pago(cid, 50, "efectivo", fecha_pago="2024-02-05", referencia="PAGO-004", observaciones="Primer pago")
            registrar_pago(cid, 55, "transferencia", fecha_pago="2025-01-18", referencia="PAGO-005", observaciones="Segundo pago")
        elif cid % 4 == 3:
            registrar_pago(cid, 165, "transferencia", fecha_pago="2025-03-25", referencia="PAGO-006", observaciones="Pago agrupado")
        else:
            # sin pagos, para que queden deudas y cuotas vencidas
            pass

    print("Datos de prueba insertados correctamente.")


# Crear tablas y sembrar datos
create_tables()
seed_data()

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Rutas
app.include_router(dashboard_router)
app.include_router(clientes_router)
app.include_router(deuda_router)
app.include_router(pagos_router)
app.include_router(exportaciones_router)