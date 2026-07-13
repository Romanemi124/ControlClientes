# 🚀 Zentry

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg">
  <img src="https://img.shields.io/badge/FastAPI-0.115-green.svg">
  <img src="https://img.shields.io/badge/SQLite-Database-blue.svg">
  <img src="https://img.shields.io/badge/HTML-CSS-orange.svg">
  <img src="https://img.shields.io/badge/JavaScript-ES6-yellow.svg">
  <img src="https://img.shields.io/badge/License-MIT-success.svg">
</p>

<p align="center">
Sistema profesional para la gestión integral de clientes, cuotas, pagos y control de deuda.
</p>

---

# 📖 Descripción

Zentry es una aplicación web desarrollada para facilitar la administración completa de clientes y el seguimiento económico de una empresa.

El sistema permite gestionar clientes, registrar cuotas mensuales, registrar pagos, controlar automáticamente las deudas pendientes y obtener estadísticas en tiempo real mediante un dashboard interactivo.

Toda la información se almacena en una base de datos SQLite y la aplicación ha sido desarrollada siguiendo una arquitectura modular basada en FastAPI, separando la lógica de negocio, la base de datos y la interfaz de usuario.

El objetivo principal es disponer de una herramienta sencilla pero potente para pequeñas y medianas empresas que necesiten controlar de forma precisa la situación económica de sus clientes.

---

# ✨ Características principales

## 👥 Gestión de clientes

- Alta de clientes.
- Modificación de clientes.
- Baja lógica de clientes.
- Gestión de clientes activos e inactivos.
- Validación automática de datos.
- Validación de teléfono según prefijo internacional.
- Validación de correo electrónico.
- Observaciones del cliente.
- Buscador inteligente.
- Ordenación por nombre o ID.
- Filtros por estado.

---

## 📅 Gestión de cuotas

El sistema permite gestionar completamente las cuotas económicas de cada cliente.

Se pueden crear dos tipos de cuotas:

- Cuotas fijas para todo el año.
- Cuotas variables por cada uno de los meses.

Características:

- Creación automática de las 12 cuotas del año.
- Importe independiente para cada mes.
- Modificación posterior de cualquier cuota.
- Estado automático de la cuota.
- Cálculo automático de deuda.
- Control anual completo.

---

## 💳 Gestión de pagos

Permite registrar todos los pagos realizados por los clientes.

Características:

- Registro manual.
- Modificación.
- Eliminación.
- Referencia del pago.
- Método de pago.
- Fecha.
- Importe.
- Observaciones.
- Aplicación automática del pago a las cuotas pendientes.

Los pagos parciales también están soportados.

---

# ⚠️ Control automático de deuda

Una de las funcionalidades principales del sistema es el cálculo automático de la deuda.

Cada vez que se registra un pago:

- se actualiza la cuota correspondiente
- se recalcula el importe pendiente
- se actualiza el estado de la cuota
- se recalcula la deuda total del cliente

No es necesario realizar ningún cálculo manual.

---

# 📊 Dashboard

El dashboard proporciona una visión global del negocio.

Indicadores disponibles:

- Total de clientes
- Clientes activos
- Clientes con deuda
- Deuda total
- Últimos pagos registrados
- Clientes con mayor deuda
- Pagos devueltos
- Cuotas vencidas
- Evolución mensual de ingresos
- Evolución mensual de deuda

Toda la información se actualiza automáticamente.

---

# 📥 Importación desde Excel

La aplicación incorpora scripts de importación masiva.

Actualmente es posible importar:

- Clientes
- Cuotas
- Pagos

Durante la importación el sistema:

- busca automáticamente cada cliente
- evita registros duplicados
- valida importes
- ignora datos incorrectos
- genera estadísticas de importación

Esto permite migrar datos históricos de forma sencilla.

---

# 📤 Exportación de datos

El sistema permite exportar información directamente a Excel.

Exportaciones disponibles:

- Histórico completo de cliente
- Clientes con deuda
- Clientes dados de alta
- Clientes dados de baja
- Histórico anual
- Histórico mensual
- Histórico diario
- Histórico entre fechas

Todos los documentos se generan automáticamente.

---

# 🏗️ Arquitectura
El proyecto sigue una arquitectura modular para facilitar el mantenimiento y la escalabilidad.
```
                Cliente (Navegador)
                       │
                       ▼
              FastAPI (Routers)
                       │
                       ▼
               Services (Lógica)
                       │
                       ▼
             SQLite (Base de Datos)
```
Cada módulo tiene una responsabilidad concreta.
```
app/
│
├── database/
│   ├── db.py
│
├── routers/
│   ├── dashboard.py
│   ├── clientes.py
│   ├── cuotas.py
│   ├── pagos.py
│   ├── deudas.py
│   ├── exportaciones.py
│
├── services/
│   ├── clientes_service.py
│   ├── cuotas_service.py
│   ├── pagos_service.py
│   ├── reportes_service.py
│
├── web/
│   ├── static/
│   │      ├── css/
│   │      ├── js/
│   │
│   ├── templates_html/
│
├── scripts/
│   ├── importar_clientes.py
│   ├── importar_cuotas.py
│   ├── importar_pagos.py
│
└── main.py
```
---
# 💾 Base de datos
La aplicación utiliza SQLite como motor de base de datos.
El modelo está dividido en cuatro tablas principales.
## Clientes
Contiene toda la información del cliente.
Campos principales:
- ID
- Nombre
- Teléfono
- Email
- Dirección
- Fecha alta
- Fecha baja
- Estado
- Observaciones
---
## Cuotas
Cada cliente dispone de una cuota por cada mes del año.
Información almacenada:
- Cliente
- Año
- Mes
- Importe previsto
- Estado
- Fecha de vencimiento
Las cuotas pueden ser:
- Fijas
- Variables
---
## Pagos
Cada pago realizado queda registrado de forma independiente.
Información almacenada:
- Cliente
- Fecha
- Importe
- Método de pago
- Referencia
---
## Aplicación de pagos
Permite relacionar un mismo pago con una o varias cuotas.
Gracias a esta tabla el sistema soporta:
- pagos parciales
- pagos superiores a una cuota
- pagos que cubren varios meses
- cálculo automático de deuda
---
# 🔄 Funcionamiento del sistema
El flujo principal es el siguiente:
```
Cliente
     │
     ▼
Registro de cuota
     │
     ▼
Registro de pago
     │
     ▼
Aplicación automática del pago
     │
     ▼
Actualización de deuda
     │
     ▼
Dashboard
```
Todo el proceso es completamente automático.
---
# ⚙️ Tecnologías utilizadas
| Tecnología | Uso |
|------------|--------------------------------|
| Python 3.12 | Lenguaje principal |
| FastAPI | Backend |
| SQLite | Base de datos |
| HTML5 | Interfaz |
| CSS3 | Diseño |
| JavaScript | Funcionalidad cliente |
| Jinja2 | Plantillas HTML |
| Pandas | Importación desde Excel |
| OpenPyXL | Lectura de Excel |
| Uvicorn | Servidor ASGI |
---
# ⚡ Instalación
Clonar el repositorio.
```bash
git clone https://github.com/USUARIO/Zentry.git
```
Entrar en el proyecto.
```bash
cd Zentry
```
Crear un entorno virtual.
Windows
```bash
python -m venv venv
```
Mac/Linux
```bash
python3 -m venv venv
```
Activar el entorno.
Windows
```bash
venv\Scripts\activate
```
Mac/Linux
```bash
source venv/bin/activate
```
Instalar dependencias.
```bash
pip install -r requirements.txt
```
---
# ▶️ Ejecución
Iniciar el servidor.
```bash
uvicorn app.main:app --reload
```
Abrir el navegador.
```
http://127.0.0.1:8000
```
La aplicación estará lista para utilizarse.
---
# 📂 Importación de datos
El proyecto incorpora scripts para importar información desde Excel.
Clientes
```bash
python scripts/importar_clientes.py
```
Cuotas
```bash
python scripts/importar_cuotas.py
```
Pagos
```bash
python scripts/importar_pagos.py
```
Todos los scripts detectan automáticamente registros duplicados y generan un resumen de la importación.

---

# 📈 Funcionalidades destacadas

## 👤 Gestión de clientes

- Alta de clientes.
- Modificación.
- Baja lógica.
- Activación y desactivación.
- Validación automática de datos.
- Buscador inteligente.
- Ordenación.
- Filtros.
- Historial completo.

---

## 📅 Gestión de cuotas

Cada cliente puede disponer de una planificación completamente personalizada.

Tipos de cuotas soportadas:

- ✅ Cuota fija para todo el año.
- ✅ Cuotas variables por cada mes.

Características:

- Creación automática de las 12 cuotas.
- Modificación posterior de cualquier mes.
- Actualización inmediata.
- Cálculo automático del estado de la cuota.
- Compatible con pagos parciales.

---

## 💳 Gestión de pagos

Permite registrar cualquier movimiento económico.

Funciones disponibles:

- Registrar pago.
- Modificar pago.
- Eliminar pago.
- Seleccionar cliente mediante buscador.
- Aplicación automática sobre cuotas.
- Historial de pagos.

Cada pago puede liquidar una o varias cuotas automáticamente.

---

## ⚠️ Gestión de deuda

La deuda se calcula en tiempo real.

Para cada cliente el sistema muestra:

- Deuda total.
- Cuotas pendientes.
- Detalle por meses.
- Estado de riesgo.

Estados disponibles:

- 🟢 Al día
- 🟡 Retraso leve
- 🟠 En riesgo
- 🔴 Moroso grave
- ⚫ Cliente dado de baja

No existe ningún cálculo manual.

---

## 📊 Dashboard

El panel principal muestra información resumida del negocio.

Indicadores:

- Número total de clientes.
- Clientes activos.
- Clientes con deuda.
- Deuda acumulada.
- Últimos pagos.
- Clientes con mayor deuda.
- Pagos devueltos.
- Cuotas vencidas.

También incluye una gráfica anual con:

- Evolución mensual de ingresos.
- Evolución mensual de deuda.

---

## 📤 Exportaciones

La aplicación permite generar informes en Excel.

Exportaciones disponibles:

- Histórico completo de un cliente.
- Histórico por día.
- Histórico por mes.
- Histórico por año.
- Histórico entre fechas.
- Clientes con deuda.
- Clientes dados de alta.
- Clientes dados de baja.

Todos los documentos mantienen un formato homogéneo y listo para su uso.

---

## 🔒 Validaciones implementadas

El sistema incorpora múltiples validaciones para garantizar la integridad de la información.

Entre ellas:

- Validación de teléfono.
- Validación de correo electrónico.
- Control de clientes duplicados.
- Control de cuotas duplicadas.
- Control de pagos duplicados.
- Importes válidos.
- Fechas válidas.
- Aplicación automática de pagos.
- Cálculo automático del estado de las cuotas.
- Actualización automática de la deuda.

---

# 🚀 Futuras mejoras

Aunque la aplicación ya ofrece una gestión completa, el diseño permite incorporar nuevas funcionalidades de forma sencilla.

Entre las mejoras previstas destacan:

- Sistema de autenticación de usuarios.
- Gestión de roles y permisos.
- Multiempresa.
- Base de datos PostgreSQL o MySQL.
- Despliegue mediante Docker.
- API REST documentada con Swagger.
- Integración con servicios de facturación.
- Notificaciones automáticas por correo electrónico.
- Recordatorios de cuotas pendientes.
- Copias de seguridad automáticas.
- Dashboard avanzado con nuevos indicadores.
- Aplicación móvil.
- Exportación a PDF.
- Integración con servicios en la nube.

---

# 🤝 Contribuciones

Las contribuciones son bienvenidas.

Si deseas colaborar:

1. Haz un Fork del proyecto.
2. Crea una nueva rama.

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza los cambios.
4. Haz commit.

```bash
git commit -m "Nueva funcionalidad"
```

5. Haz push.

```bash
git push origin feature/nueva-funcionalidad
```

6. Abre un Pull Request.

---

# 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT.

Consulta el archivo **LICENSE** para más información.

---

# 👨‍💻 Autor

**Emilio José Román Rosales**

🎓 Grado en Ingeniería Informática

💻 Desarrollador Full Stack

---

# ⭐ Si este proyecto te resulta útil...

No olvides darle una ⭐ al repositorio.

¡Gracias por visitar **Zentry**!
