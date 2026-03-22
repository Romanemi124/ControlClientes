import random
from app.services.clientes_service import crear_cliente, obtener_clientes
from app.services.pagos_service import crear_cuota, registrar_pago


NOMBRES = [
    "Juan", "Ana", "Luis", "Marta", "Carlos",
    "Lucía", "Pedro", "Elena", "Jorge", "Laura"
]


def generar_clientes_y_datos(num_clientes=50):
    print("Generando clientes...")

    # Crear clientes
    for i in range(num_clientes):
        nombre = random.choice(NOMBRES) + f" {i}"
        telefono = f"600{random.randint(100000, 999999)}"
        email = f"cliente{i}@email.com"
        direccion = f"Calle {i}"

        crear_cliente(nombre, telefono, email, direccion, "2026-01-01")

    clientes = obtener_clientes()

    print("Generando cuotas y pagos...")

    for cliente in clientes:
        cliente_id = cliente["id"]

        # Crear 12 meses
        for mes in range(1, 13):
            crear_cuota(cliente_id, 2026, mes, 50)

        # Simular pagos
        tipo_pago = random.choice(["completo", "parcial", "nada"])

        if tipo_pago == "completo":
            registrar_pago(cliente_id, 600, "transferencia")  # paga todo

        elif tipo_pago == "parcial":
            registrar_pago(cliente_id, random.randint(50, 400), "efectivo")

        # "nada" → no paga

    print("Datos generados correctamente")