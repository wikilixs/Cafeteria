import logging
from decimal import Decimal
from fastapi import HTTPException
from services.stock_service import verificar_stock_minimos

logger = logging.getLogger(__name__)


def _obtener_lotes_fifo(conn, id_insumo: int) -> list[dict]:
    """Lotes disponibles ordenados FEFO (vence antes primero), luego FIFO."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_detalle_compra, cantidad_disponible, costo_unitario, fecha_vencimiento
            FROM detalle_compra
            WHERE id_insumo = %s AND cantidad_disponible > 0
            ORDER BY fecha_vencimiento ASC NULLS LAST, id_detalle_compra ASC
            """,
            (id_insumo,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def _validar_stock(conn, insumos_necesarios: dict) -> None:
    """Valida que haya stock suficiente para todos los insumos. Lanza error si no."""
    with conn.cursor() as cur:
        for id_insumo, cantidad_necesaria in insumos_necesarios.items():
            cur.execute(
                """
                SELECT i.nombre, COALESCE(SUM(dc.cantidad_disponible), 0) AS stock
                FROM insumo i
                LEFT JOIN detalle_compra dc ON dc.id_insumo = i.id_insumo
                WHERE i.id_insumo = %s
                GROUP BY i.nombre
                """,
                (id_insumo,)
            )
            row = cur.fetchone()
            nombre = row[0]
            stock  = Decimal(str(row[1]))

            if stock < cantidad_necesaria:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente: '{nombre}'. "
                           f"Disponible: {stock}, requerido: {cantidad_necesaria}"
                )


def _descontar_insumo(conn, id_insumo: int, cantidad_necesaria: Decimal) -> list[dict]:
    """
    Descuenta un insumo de sus lotes en orden FIFO/FEFO.
    Retorna lista de consumos por lote.
    """
    lotes    = _obtener_lotes_fifo(conn, id_insumo)
    consumos = []
    restante = cantidad_necesaria

    with conn.cursor() as cur:
        for lote in lotes:
            if restante <= 0:
                break

            disponible = Decimal(str(lote["cantidad_disponible"]))
            a_consumir = min(disponible, restante)

            cur.execute(
                """
                UPDATE detalle_compra
                SET cantidad_disponible = cantidad_disponible - %s
                WHERE id_detalle_compra = %s
                """,
                (a_consumir, lote["id_detalle_compra"])
            )

            consumos.append({
                "id_detalle_compra": lote["id_detalle_compra"],
                "cantidad":          a_consumir
            })
            restante -= a_consumir

    return consumos


def registrar_venta(conn, id_usuario: int, detalles: list[dict]) -> dict:
    """
    Registra una venta completa:
      1. Obtiene recetas de los productos
      2. Valida stock antes de tocar la BD
      3. Inserta venta y detalles
      4. Descuenta insumos FIFO/FEFO
      5. Registra consumo_lotes
      6. Verifica stock mínimo y retorna alertas

    detalles: lista de dicts con keys:
        id_producto, cantidad, precio_unitario
    """
    if not detalles:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un detalle")

    try:
        with conn.cursor() as cur:

            # 1. Obtener recetas de todos los productos
            ids_productos = [d["id_producto"] for d in detalles]
            cur.execute(
                """
                SELECT id_producto, id_insumo, cantidad
                FROM producto_insumo
                WHERE id_producto = ANY(%s)
                """,
                (ids_productos,)
            )
            recetas = cur.fetchall()  # (id_producto, id_insumo, cantidad)

        # 2. Calcular insumos totales necesarios
        insumos_necesarios: dict[int, Decimal] = {}
        for detalle in detalles:
            cantidad_vendida = Decimal(str(detalle["cantidad"]))
            for rec in recetas:
                if rec[0] == detalle["id_producto"]:
                    id_insumo       = rec[1]
                    cantidad_insumo = Decimal(str(rec[2])) * cantidad_vendida
                    insumos_necesarios[id_insumo] = (
                        insumos_necesarios.get(id_insumo, Decimal("0")) + cantidad_insumo
                    )

        # 3. Validar stock ANTES de insertar nada
        _validar_stock(conn, insumos_necesarios)

        # 4. Calcular total
        total = sum(
            Decimal(str(d["cantidad"])) * Decimal(str(d["precio_unitario"]))
            for d in detalles
        )
        logger.info(f"Registrando venta — total: {total}")

        with conn.cursor() as cur:

            # 5. Insertar venta
            cur.execute(
                """
                INSERT INTO venta (id_usuario, estado)
                VALUES (%s, 'PAGADA')
                RETURNING id_venta
                """,
                (id_usuario,)
            )
            id_venta = cur.fetchone()[0]

            # 6. Insertar detalles + descontar insumos por lote
            for detalle in detalles:
                cantidad_vendida = Decimal(str(detalle["cantidad"]))

                cur.execute(
                    """
                    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_detalle_venta
                    """,
                    (id_venta, detalle["id_producto"], cantidad_vendida,
                     Decimal(str(detalle["precio_unitario"])))
                )
                id_detalle_venta = cur.fetchone()[0]

                # Descontar cada insumo de la receta
                for rec in recetas:
                    if rec[0] != detalle["id_producto"]:
                        continue

                    id_insumo       = rec[1]
                    cantidad_insumo = Decimal(str(rec[2])) * cantidad_vendida
                    consumos        = _descontar_insumo(conn, id_insumo, cantidad_insumo)

                    # Registrar consumo_lotes
                    for consumo in consumos:
                        cur.execute(
                            """
                            INSERT INTO consumo_lotes (id_detalle_venta, id_detalle_compra, cantidad)
                            VALUES (%s, %s, %s)
                            """,
                            (id_detalle_venta, consumo["id_detalle_compra"], consumo["cantidad"])
                        )

            conn.commit()

        # 7. Verificar stock mínimo post-venta
        alertas = verificar_stock_minimos(conn)
        if alertas:
            logger.warning(f"Alertas de stock mínimo: {[a['nombre'] for a in alertas]}")

        logger.info(f"Venta {id_venta} registrada correctamente")
        return {
            "id_venta":             id_venta,
            "total":                total,
            "alertas_stock_minimo": alertas
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error registrando venta: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar la venta")
