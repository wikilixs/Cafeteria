import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def _obtener_o_crear_insumo(cur, nombre, unidad, cantidad):
    """
    Busca un insumo por nombre.
    - Si existe: retorna su id_insumo (el stock se actualiza después).
    - Si no existe: lo crea con stock=0 y activo=True, retorna el nuevo id_insumo.
    La unidad es obligatoria solo cuando se crea; si el insumo ya existe se ignora.
    """
    await cur.execute(
        "SELECT id_insumo FROM insumo WHERE nombre = %s",
        (nombre,)
    )
    row = await cur.fetchone()
    if row:
        return row["id_insumo"]

    # Insumo nuevo: se crea con stock=0, la compra le sumará el stock a continuación
    if not unidad:
        raise HTTPException(
            status_code=400,
            detail=f"El insumo '{nombre}' no existe. Debes indicar 'unidad' para crearlo."
        )

    await cur.execute(
        """
        INSERT INTO insumo (nombre, unidad, stock, activo)
        VALUES (%s, %s, 0, TRUE)
        RETURNING id_insumo
        """,
        (nombre, unidad)
    )
    nuevo = await cur.fetchone()
    logger.info(f"Insumo nuevo creado: '{nombre}' (id={nuevo['id_insumo']})")
    return nuevo["id_insumo"]


async def registrar_compra(conn, id_proveedor, id_usuario, detalles, observacion=None):
    """
    Registra una compra con detalles de insumos y actualiza el stock.

    Cada detalle debe tener:
      - nombre        : nombre del insumo (se crea automáticamente si no existe)
      - cantidad      : cantidad comprada
      - costo_unitario: costo por unidad
      - unidad        : unidad de medida (requerida solo si el insumo es nuevo)

    Secuencia requerida antes de llamar:
      1. Crear rol → personal → usuario  (POST /personal/crear con crear_usuario: true)
      2. Crear proveedor (opcional)       (POST /proveedor/)
      3. Llamar este endpoint — los insumos se crean automáticamente
    """
    if not detalles:
        raise HTTPException(status_code=400, detail="Detalles requeridos")

    try:
        cur = conn.cursor()

        # Validar usuario
        await cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
        if not await cur.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con id {id_usuario} no encontrado. "
                       f"Crea el empleado primero con POST /personal/crear (crear_usuario: true)."
            )

        # Validar proveedor (si se especificó)
        if id_proveedor is not None:
            await cur.execute(
                "SELECT id_proveedor FROM proveedor WHERE id_proveedor = %s AND activo = TRUE",
                (id_proveedor,)
            )
            if not await cur.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Proveedor con id {id_proveedor} no encontrado o inactivo. "
                           f"Créalo con POST /proveedor/ o usa null para omitirlo."
                )

        # 1. Insertar cabecera de compra
        await cur.execute(
            """
            INSERT INTO compra (id_proveedor, id_usuario, fecha, observacion)
            VALUES (%s, %s, NOW(), %s)
            RETURNING id_compra
            """,
            (id_proveedor, id_usuario, observacion)
        )
        row = await cur.fetchone()
        id_compra = row["id_compra"]

        insumos_afectados = []

        # 2. Procesar cada detalle
        for d in detalles:
            nombre = d["nombre"]
            cantidad = d["cantidad"]
            costo_unitario = d["costo_unitario"]
            unidad = d.get("unidad")

            # Resolver insumo (crear si no existe)
            id_insumo = await _obtener_o_crear_insumo(cur, nombre, unidad, cantidad)

            # Insertar detalle de compra
            await cur.execute(
                """
                INSERT INTO detalle_compra (id_compra, id_insumo, cantidad, costo_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (id_compra, id_insumo, cantidad, costo_unitario)
            )

            # Actualizar stock del insumo
            await cur.execute(
                """
                UPDATE insumo SET stock = stock + %s WHERE id_insumo = %s
                RETURNING id_insumo, nombre, unidad, stock
                """,
                (cantidad, id_insumo)
            )
            insumo_actualizado = await cur.fetchone()
            insumos_afectados.append({
                "id_insumo": insumo_actualizado["id_insumo"],
                "nombre": insumo_actualizado["nombre"],
                "unidad": insumo_actualizado["unidad"],
                "stock_actual": float(insumo_actualizado["stock"]),
                "cantidad_comprada": float(cantidad),
                "costo_unitario": float(costo_unitario),
            })

        await conn.commit()
        return {
            "id_compra": id_compra,
            "insumos": insumos_afectados
        }

    except HTTPException:
        await conn.rollback()
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error al registrar compra: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
