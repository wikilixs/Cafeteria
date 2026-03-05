import logging
from decimal import Decimal
from fastapi import HTTPException
from services.stock_service import verificar_stock_minimos
from typing import Optional

logger = logging.getLogger(__name__)


async def _obtener_lotes_fifo(conn, id_insumo: int) -> list[dict]:
    """Lotes disponibles ordenados FEFO (vence antes primero), luego FIFO."""
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id_detalle_compra, cantidad_disponible, costo_unitario, fecha_vencimiento
            FROM detalle_compra
            WHERE id_insumo = %s AND cantidad_disponible > 0
            ORDER BY fecha_vencimiento ASC NULLS LAST, id_detalle_compra ASC
            """,
            (id_insumo,)
        )
        cols = [desc[0] for desc in cur.description]
        rows = await cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]


async def _validar_stock(conn, insumos_necesarios: dict) -> None:
    """Valida que haya stock suficiente para todos los insumos. Lanza error si no."""
    async with conn.cursor() as cur:
        for id_insumo, cantidad_necesaria in insumos_necesarios.items():
            await cur.execute(
                """
                SELECT i.nombre, COALESCE(SUM(dc.cantidad_disponible), 0) AS stock
                FROM insumo i
                LEFT JOIN detalle_compra dc ON dc.id_insumo = i.id_insumo
                WHERE i.id_insumo = %s
                GROUP BY i.nombre
                """,
                (id_insumo,)
            )
            row = await cur.fetchone()
            nombre = row[0]
            stock  = Decimal(str(row[1]))

            if stock < cantidad_necesaria:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente: '{nombre}'. "
                           f"Disponible: {stock}, requerido: {cantidad_necesaria}"
                )


async def _descontar_insumo(conn, id_insumo: int, cantidad_necesaria: Decimal) -> list[dict]:
    """
    Descuenta un insumo de sus lotes en orden FIFO/FEFO.
    Retorna lista de consumos por lote.
    """
    lotes    = await _obtener_lotes_fifo(conn, id_insumo)
    consumos = []
    restante = cantidad_necesaria

    async with conn.cursor() as cur:
        for lote in lotes:
            if restante <= 0:
                break

            disponible = Decimal(str(lote["cantidad_disponible"]))
            a_consumir = min(disponible, restante)

            await cur.execute(
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


async def registrar_venta(conn, id_usuario: int, detalles: list[dict]) -> dict:
    """
    Registra una venta completa:
      1. Inserta venta y detalles

    detalles: lista de dicts con keys:
        id_producto, cantidad, precio_unitario
    """
    if not detalles:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un detalle")

    try:
        # 2. Calcular total
        total = sum(
            Decimal(str(d["cantidad"])) * Decimal(str(d["precio_unitario"]))
            for d in detalles
        )
        logger.info(f"Registrando venta — total: {total}")

        async with conn.cursor() as cur:

            # 5. Insertar venta
            await cur.execute(
                """
                INSERT INTO venta (id_usuario, estado, total)
                VALUES (%s, 'PAGADA', %s)
                RETURNING id_venta
                """,
                (id_usuario, total)
            )
            id_venta_result = await cur.fetchone()
            id_venta = id_venta_result['id_venta']

            # 6. Insertar detalles
            for detalle in detalles:
                cantidad_vendida = Decimal(str(detalle["cantidad"]))

                await cur.execute(
                    """
                    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_detalle_venta
                    """,
                    (id_venta, detalle["id_producto"], cantidad_vendida,
                     Decimal(str(detalle["precio_unitario"])))
                )

        await conn.commit()

        logger.info(f"Venta {id_venta} registrada correctamente")
        return {
            "id_venta":             id_venta,
            "total":                total
        }

    except HTTPException:
        await conn.rollback()
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error registrando venta: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar la venta")

async def obtener_reporte_ventas(conn, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, id_usuario: Optional[int] = None) -> list[dict]:
    """
    Obtiene un reporte de ventas con detalles, opcionalmente filtrado por fechas y usuario.
    """
    consulta = """
        SELECT 
            v.id_venta,
            v.fecha,
            v.estado,
            v.total,
            v.nota,
            u.nombre AS usuario,
            dv.id_producto,
            pr.nombre AS producto,
            dv.cantidad,
            dv.precio_unitario,
            (dv.cantidad * dv.precio_unitario) AS subtotal
        FROM venta v
        JOIN usuario u ON v.id_usuario = u.id_usuario
        JOIN detalle_venta dv ON v.id_venta = dv.id_venta
        JOIN producto pr ON dv.id_producto = pr.id_producto
        WHERE 1=1
    """
    params = []

    if fecha_inicio:
        consulta += " AND v.fecha >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        consulta += " AND v.fecha <= %s"
        params.append(fecha_fin)
    if id_usuario:
        consulta += " AND v.id_usuario = %s"
        params.append(id_usuario)

    consulta += " ORDER BY v.fecha DESC, v.id_venta DESC"

    try:
        async with conn.cursor() as cur:
            await cur.execute(consulta, params)
            cols = [desc[0] for desc in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        logger.error(f"Error obteniendo reporte de ventas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener el reporte de ventas")