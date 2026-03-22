from app.database.models import create_tables
from app.utils.excel_export import (
    exportar_historico_detallado_cliente_excel,
    exportar_historico_detallado_cliente_por_mes_excel,
    exportar_historico_detallado_cliente_por_anio_excel,
    exportar_historico_detallado_cliente_por_dia_excel,
    exportar_historico_detallado_cliente_entre_fechas_excel,
    exportar_historico_mes_excel,
    exportar_historico_anio_excel,
    exportar_historico_dia_excel,
    exportar_historico_entre_fechas_excel,
    exportar_clientes_con_deuda_excel,
    exportar_clientes_baja_con_deuda_excel,
    exportar_clientes_dados_de_alta_excel,
    exportar_clientes_dados_de_baja_excel,
)


def main():
    create_tables()
    print("Base de datos lista")

    # ========================================
    # 1. Histórico detallado de un solo cliente
    # ========================================
    exportar_historico_detallado_cliente_excel(1)

    # Mismo cliente, filtrado por mes
    exportar_historico_detallado_cliente_por_mes_excel(1, 2026, 3)

    # Mismo cliente, filtrado por año
    exportar_historico_detallado_cliente_por_anio_excel(1, 2026)

    # Mismo cliente, filtrado por día
    exportar_historico_detallado_cliente_por_dia_excel(1, "2026-03-31")

    # Mismo cliente, entre fechas
    exportar_historico_detallado_cliente_entre_fechas_excel(1, "2026-01-01", "2026-06-30")

    # ========================================
    # 2. Histórico global detallado
    # ========================================
    exportar_historico_mes_excel(2026, 3)
    exportar_historico_anio_excel(2026)
    exportar_historico_dia_excel("2026-03-31")
    exportar_historico_entre_fechas_excel("2026-01-01", "2026-06-30")

    # ========================================
    # 6 y 7. Deuda
    # ========================================
    exportar_clientes_con_deuda_excel()
    exportar_clientes_baja_con_deuda_excel()

    # ========================================
    # 8 y 9. Altas y bajas
    # ========================================
    exportar_clientes_dados_de_alta_excel()
    exportar_clientes_dados_de_baja_excel()


if __name__ == "__main__":
    main()