
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

# Crear tablas
with open("crm_schema.sql", "r") as f:
    cursor.executescript(f.read())

# Insertar datos de ejemplo

clientes = [('Juan', 'Pérez', 'juan.perez@example.com', '555-1234', 'Calle Falsa 123'),
            ('María', 'Gómez', 'maria.gomez@example.com', '555-5678', 'Avenida Siempre Viva 742'),
            ('Carlos', 'López', 'carlos.lopez@example.com', '555-8765', 'Boulevard de los Sueños 456'),
            ('Ana', 'Martínez', 'ana.martinez@example.com', '555-4321', 'Calle Luna 789'),
            ('Luis', 'Ramírez', 'luis.ramirez@example.com', '555-9876', 'Avenida Sol 321')]

pedidos = [ ('2025-05-01', 'Laptop Dell', 1200.00, 'Pagado', 1),
            ('2025-05-03', 'Mouse Logitech', 25.00, 'Pendiente', 1),
            ('2025-05-05', 'Teclado Mecánico', 75.00, 'Cancelado', 1),
            ('2025-05-07', 'Monitor Samsung', 300.00, 'Pagado', 2),
            ('2025-05-10', 'Impresora HP', 150.00, 'Pendiente', 2),
            ('2025-05-12', 'Tablet Apple', 500.00, 'Pagado', 2),
            ('2025-05-15', 'Auriculares Sony', 80.00, 'Cancelado', 3),
            ('2025-05-18', 'Cámara Canon', 600.00, 'Pagado', 3),
            ('2025-05-20', 'Disco Duro Externo', 100.00, 'Pendiente', 1), 
            ('2025-05-22', 'Cargador Universal', 30.00, 'Pagado', 1),    
            ('2025-05-25', 'Router WiFi', 60.00, 'Pagado', 2),           
            ('2025-05-28', 'Smartwatch', 200.00, 'Pendiente', 2),        
            ('2025-05-30', 'Altavoces Bluetooth', 120.00, 'Pagado', 3),  
            ('2025-05-31', 'Proyector', 350.00, 'Pendiente', 3),         
            ('2025-05-02', 'SSD 1TB', 150.00, 'Pagado', 4),              
            ('2025-05-04', 'Tarjeta Gráfica', 400.00, 'Pendiente', 4),   
            ('2025-05-06', 'Memoria RAM 16GB', 80.00, 'Pagado', 4),      
            ('2025-05-08', 'Teclado Inalámbrico', 45.00, 'Cancelado', 4),
            ('2025-05-09', 'Monitor 4K', 500.00, 'Pagado', 4),           
            ('2025-05-11', 'Impresora 3D', 700.00, 'Pendiente', 5),      
            ('2025-05-13', 'Cámara de Seguridad', 250.00, 'Pagado', 5),  
            ('2025-05-14', 'Micrófono Profesional', 150.00, 'Pendiente', 5), 
            ('2025-05-16', 'Consola de Videojuegos', 300.00, 'Pagado', 5),   
            ('2025-05-17', 'Tablet Samsung', 350.00, 'Cancelado', 5)]        

cursor.executemany("""
    INSERT INTO clientes (nombre, apellido, email, telefono, direccion)
    VALUES (?, ?, ?, ?, ?)
""", clientes)

cursor.executemany("""
    INSERT INTO pedidos (fecha, descripcion, monto, estado, cliente_id)
    VALUES (?, ?, ?, ?, ?)
""", pedidos)

conn.commit()
conn.close()
