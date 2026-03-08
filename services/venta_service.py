import logging
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def _obtener_o_crear_cliente(cur, id_cliente=None, nombre_cliente=None, nit_cliente=None):

    if id_cliente:
        await cur.execute("SELECT id_cliente FROM cliente WHERE id_cliente = %s", (id_cliente,))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Cliente con id {id_cliente} no encontrado")
        return id_cliente

    if not nombre_cliente:
        raise HTTPException(
            status_code=400,
            detail="Se requiere id_cliente o nombre_cliente para registrar la venta"
        )

    await cur.execute(
        "INSERT INTO cliente (nombre, nit, activo) VALUES (%s, %s, TRUE) RETURNING id_cliente",
        (nombre_cliente, nit_cliente)
    )
    row = await cur.fetchone()
    logger.info(f"Cliente nuevo creado: '{nombre_cliente}' (id={row['id_cliente']})")
    return row["id_cliente"]


async def _validar_prerequisitos(cur, id_usuario, id_estado, detalles):

    # 1. Validar usuario
    await cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
    if not await cur.fetchone():
        raise HTTPException(
            status_code=404,
            detail=f"Usuario con id {id_usuario} no encontrado. "
                   f"Crea el empleado primero con POST /personal/crear (crear_usuario: true)."
        )

    # 2. Validar estado de venta
    await cur.execute("SELECT id_estado FROM estado_venta WHERE id_estado = %s", (id_estado,))
    if not await cur.fetchone():
        raise HTTPException(
            status_code=404,
            detail=f"Estado de venta con id {id_estado} no encontrado. "
                   f"Los estados disponibles son: 1=COMPLETADA, 2=CANCELADA, 3=PENDIENTE."
        )

    # 3. Validar cada producto
    for d in detalles:
        await cur.execute(
            "SELECT id_producto, nombre FROM producto WHERE id_producto = %s AND activo = TRUE",
            (d["id_producto"],)
        )
        if not await cur.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Producto con id {d['id_producto']} no encontrado o inactivo. "
                       f"Créalo primero con POST /producto/."
            )


async def registrar_venta(conn, id_usuario, id_cliente, id_estado, metodo_pago, detalles,
                          nombre_cliente=None, nit_cliente=None):
    if not detalles:
        raise HTTPException(status_code=400, detail="Detalles requeridos")

    try:
        cur = conn.cursor()

        # 1. Validaciones previas (usuario, estado, productos)
        await _validar_prerequisitos(cur, id_usuario, id_estado, detalles)

        # 2. Resolver cliente (existente o crear nuevo)
        id_cliente_final = await _obtener_o_crear_cliente(cur, id_cliente, nombre_cliente, nit_cliente)

        # 3. Calcular total
        total = sum(
            Decimal(str(d["cantidad"])) * Decimal(str(d["precio_unitario"]))
            for d in detalles
        )

        # 4. Insertar venta
        await cur.execute(
            """
            INSERT INTO venta (id_usuario, id_cliente, id_estado, metodo_pago, fecha)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id_venta
            """,
            (id_usuario, id_cliente_final, id_estado, metodo_pago)
        )
        row = await cur.fetchone()
        id_venta = row["id_venta"]

        # 5. Insertar detalles y restar stock según receta
        for d in detalles:
            await cur.execute(
                """
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (id_venta, d["id_producto"], d["cantidad"], d["precio_unitario"])
            )

            # Descontar stock de insumos según receta
            await cur.execute(
                "SELECT id_insumo, cantidad FROM receta WHERE id_producto = %s",
                (d["id_producto"],)
            )
            receta = await cur.fetchall()

            for insumo in receta:
                cant_total = Decimal(str(insumo["cantidad"])) * Decimal(str(d["cantidad"]))
                await cur.execute(
                    "UPDATE insumo SET stock = stock - %s WHERE id_insumo = %s",
                    (cant_total, insumo["id_insumo"])
                )

        await conn.commit()
        return {
            "id_venta": id_venta,
            "id_cliente": id_cliente_final,
            "total": float(total)
        }

    except HTTPException:
        await conn.rollback()
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error al registrar venta: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))