CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    prefijo TEXT DEFAULT '+34',
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    fecha_alta TEXT,
    fecha_baja TEXT,
    activo INTEGER DEFAULT 1,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS cuotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    anio INTEGER,
    mes INTEGER,
    importe_previsto REAL,
    estado_cuota TEXT,
    fecha_vencimiento TEXT,
    observaciones TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    fecha_pago TEXT,
    importe_pagado REAL,
    metodo_pago TEXT,
    referencia TEXT,
    observaciones TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS aplicacion_pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pago_id INTEGER,
    cuota_id INTEGER,
    importe_aplicado REAL,
    FOREIGN KEY(pago_id) REFERENCES pagos(id),
    FOREIGN KEY(cuota_id) REFERENCES cuotas(id)
);