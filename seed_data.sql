
INSERT INTO rol (nombre) VALUES
    ('Administrador'),
    ('Cajero'),
    ('Cocinero')
    ('Mesero')
    ('Barista')
    ('Encargado de Almacén')
    ('Encargado de Limpieza');


-- ============================================================
-- 3. PERSONAL
-- ============================================================
INSERT INTO personal (id_rol, ci, nombres, primer_apellido, segundo_apellido, fecha_nacimiento, telefono, activo, fecha_ingreso) VALUES
    (1, 12345678, 'Carlos',   'Mamani',  'Quispe',    '1990-05-15', 70012345, TRUE, '2022-01-10'),
    (2, 87654321, 'Ana',      'Flores',  'Torrez',    '1995-09-20', 70098765, TRUE, '2023-03-01'),
    (3, 11223344, 'Luis',     'Condori', 'Apaza',     '1988-11-30', 70011223, TRUE, '2021-06-15'),
    (2, 44332211, 'Paola',    'Choque',  'Limachi',   '1998-02-14', 70044332, TRUE, '2024-01-05');


-- ============================================================
-- 4. USUARIOS (password_hash = últimos 6 dígitos del CI como texto plano para pruebas)
-- ============================================================
INSERT INTO usuario (id_personal, email, password_hash, activo) VALUES
    (1, 'carlos.mamani@cafeteria.com',  '345678', TRUE),
    (2, 'ana.flores@cafeteria.com',     '654321', TRUE),
    (3, 'luis.condori@cafeteria.com',   '223344', TRUE);


-- ============================================================
-- 5. CLIENTES
-- ============================================================
INSERT INTO cliente (nombre, nit, activo) VALUES
    ('Cliente General',    NULL,        TRUE),
    ('Juan Quispe',        '12345678',  TRUE),
    ('María Condori',      '98765432',  TRUE),
    ('Empresa ABC S.R.L.', '1023456780',TRUE);


-- ============================================================
-- 6. PROVEEDORES
-- ============================================================
INSERT INTO proveedor (nombre, nit, telefono, email, direccion, activo) VALUES
    ('Distribuidora El Paraíso', 1234567, 71234567, 'paraiso@gmail.com',    'Av. Heroínas 123',     TRUE),
    ('Lacteos del Norte S.A.',   9876543, 79876543, 'lacteos@norte.com',    'Calle Bolívar 456',    TRUE),
    ('Importadora Central',      5551234, 75551234,  NULL,                  'Mercado Central L-12', TRUE);


-- ============================================================
-- 7. CATEGORÍAS DE PRODUCTO
-- ============================================================
INSERT INTO categoria_producto (nombre) VALUES
    ('Bebidas Calientes'),
    ('Bebidas Frías'),
    ('Sándwiches'),
    ('Postres'),
    ('Desayunos');


-- ============================================================
-- 8. PRODUCTOS
-- ============================================================
INSERT INTO producto (id_categoria, nombre, costo, precio_venta, activo) VALUES
    (1, 'Café Americano',        3.50,  8.00,  TRUE),
    (1, 'Café con Leche',        5.00,  10.00, TRUE),
    (1, 'Té Verde',              2.00,  7.00,  TRUE),
    (2, 'Jugo de Naranja',       4.00,  9.00,  TRUE),
    (2, 'Smoothie de Fresa',     6.00,  14.00, TRUE),
    (3, 'Sándwich de Jamón',     8.00,  18.00, TRUE),
    (3, 'Sándwich Vegetal',      7.00,  16.00, TRUE),
    (4, 'Brownie de Chocolate',  4.50,  12.00, TRUE),
    (5, 'Desayuno Completo',    18.00,  35.00, TRUE);


-- ============================================================
-- 9. INSUMOS
-- ============================================================
INSERT INTO insumo (nombre, unidad, stock, activo) VALUES
    ('Café molido',      'g',      500.00,  TRUE),
    ('Leche',            'ml',    2000.00,  TRUE),
    ('Azúcar',           'g',     1000.00,  TRUE),
    ('Té verde en bolsa','unidad',   50.00, TRUE),
    ('Naranja',          'unidad',   30.00, TRUE),
    ('Fresa',            'g',      300.00,  TRUE),
    ('Pan de molde',     'unidad',   20.00, TRUE),
    ('Jamón',            'g',      400.00,  TRUE),
    ('Tomate',           'g',      200.00,  TRUE),
    ('Lechuga',          'g',      150.00,  TRUE),
    ('Harina',           'g',      500.00,  TRUE),
    ('Chocolate',        'g',      300.00,  TRUE),
    ('Huevo',            'unidad',  12.00,  TRUE);


-- ============================================================
-- 10. RECETAS (insumos necesarios por producto)
-- ============================================================
-- Café Americano (id_producto=1)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (1, 1, 15.00); -- 15g café
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (1, 3, 10.00); -- 10g azúcar

-- Café con Leche (id_producto=2)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (2, 1, 12.00); -- 12g café
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (2, 2, 150.00);-- 150ml leche
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (2, 3, 8.00);  -- 8g azúcar

-- Té Verde (id_producto=3)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (3, 4, 1.00);  -- 1 bolsita
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (3, 3, 5.00);  -- 5g azúcar

-- Jugo de Naranja (id_producto=4)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (4, 5, 3.00);  -- 3 naranjas

-- Smoothie de Fresa (id_producto=5)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (5, 6, 100.00);-- 100g fresa
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (5, 2, 100.00);-- 100ml leche
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (5, 3, 10.00); -- 10g azúcar

-- Sándwich de Jamón (id_producto=6)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (6, 7, 2.00);  -- 2 panes
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (6, 8, 60.00); -- 60g jamón
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (6, 9, 30.00); -- 30g tomate

-- Sándwich Vegetal (id_producto=7)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (7, 7, 2.00);  -- 2 panes
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (7, 9, 40.00); -- 40g tomate
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (7, 10, 30.00);-- 30g lechuga

-- Brownie de Chocolate (id_producto=8)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (8, 11, 80.00);-- 80g harina
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (8, 12, 50.00);-- 50g chocolate
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (8, 13, 1.00); -- 1 huevo
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (8, 3, 30.00); -- 30g azúcar

-- Desayuno Completo (id_producto=9)
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (9, 1, 10.00); -- café
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (9, 2, 100.00);-- leche
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (9, 7, 2.00);  -- pan
INSERT INTO receta (id_producto, id_insumo, cantidad) VALUES (9, 13, 2.00); -- huevos


-- ============================================================
-- 11. COMPRA DE INSUMOS (reabastecimiento inicial)
-- ============================================================
INSERT INTO compra (id_proveedor, id_usuario, fecha, observacion) VALUES
    (1, 1, NOW() - INTERVAL '5 days', 'Compra inicial de café y azúcar'),
    (2, 1, NOW() - INTERVAL '3 days', 'Reabastecimiento de lácteos'),
    (3, 2, NOW() - INTERVAL '1 day',  'Compra de panadería y varios');

INSERT INTO detalle_compra (id_compra, id_insumo, cantidad, costo_unitario) VALUES
    (1, 1, 1000.00, 0.08),   -- 1000g café a 0.08 Bs/g
    (1, 3,  500.00, 0.01),   -- 500g azúcar
    (2, 2, 5000.00, 0.005),  -- 5 litros leche
    (2, 6,  300.00, 0.05),   -- 300g fresa
    (3, 7,   50.00, 1.50),   -- 50 panes
    (3, 8,  500.00, 0.12),   -- 500g jamón
    (3, 9,  500.00, 0.02),   -- 500g tomate
    (3, 10, 200.00, 0.03);   -- 200g lechuga

-- ============================================================
-- 12. VENTAS DE EJEMPLO
-- ============================================================

INSERT INTO estado_venta (nombre) VALUES
    ('PENDIENTE'),
    ('CANCELADA'),
    ('COMPLETADA');

INSERT INTO venta (id_usuario, id_cliente, id_estado, metodo_pago, fecha) VALUES
    (2, 1, 1, 'EFECTIVO', NOW() - INTERVAL '2 days'),
    (2, 2, 1, 'EFECTIVO',       NOW() - INTERVAL '1 day'),
    (3, 3, 3, 'EFECTIVO',  NOW());

INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (1, 1, 2,  8.00),   -- 2 cafés americanos
    (1, 6, 1, 18.00),   -- 1 sándwich jamón
    (2, 2, 1, 10.00),   -- café con leche
    (2, 8, 2, 12.00),   -- 2 brownies
    (3, 9, 1, 35.00);   -- 1 desayuno completo (pendiente)


-- ============================================================
--  VERIFICAR DATOS INSERTADOS
-- ============================================================
SELECT 'rol'                AS tabla, COUNT(*) FROM rol               UNION ALL
SELECT 'personal'           AS tabla, COUNT(*) FROM personal          UNION ALL
SELECT 'usuario'            AS tabla, COUNT(*) FROM usuario           UNION ALL
SELECT 'cliente'            AS tabla, COUNT(*) FROM cliente           UNION ALL
SELECT 'proveedor'          AS tabla, COUNT(*) FROM proveedor         UNION ALL
SELECT 'categoria_producto' AS tabla, COUNT(*) FROM categoria_producto UNION ALL
SELECT 'producto'           AS tabla, COUNT(*) FROM producto          UNION ALL
SELECT 'insumo'             AS tabla, COUNT(*) FROM insumo            UNION ALL
SELECT 'receta'             AS tabla, COUNT(*) FROM receta            UNION ALL
SELECT 'compra'             AS tabla, COUNT(*) FROM compra            UNION ALL
SELECT 'detalle_compra'     AS tabla, COUNT(*) FROM detalle_compra    UNION ALL
SELECT 'estado_venta'       AS tabla, COUNT(*) FROM estado_venta      UNION ALL
SELECT 'venta'              AS tabla, COUNT(*) FROM venta             UNION ALL
SELECT 'detalle_venta'      AS tabla, COUNT(*) FROM detalle_venta;
