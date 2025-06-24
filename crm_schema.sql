CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE CHECK (email LIKE '%@%'and email LIKE '%.%'),
    telefono TEXT,
    direccion TEXT,
    fecha_registro DATE DEFAULT (DATE('now'))
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE DEFAULT (DATE('now')),
    descripcion TEXT NOT NULL,
    monto INTEGER NOT NULL CHECK (monto > 0),
    estado TEXT NOT NULL CHECK (estado IN ('Pendiente', 'Pagado', 'Cancelado')),
    cliente_id INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);


