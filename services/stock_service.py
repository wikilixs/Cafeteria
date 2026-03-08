import logging

logger = logging.getLogger(__name__)



async def obtener_stock_insumo(conn, id_insumo: int) -> float:
    """Retorna el stock actual de un insumo."""
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT stock
                FROM insumo
                WHERE id_insumo = %s
                """,
                (id_insumo,)
            )
            result = await cur.fetchone()
            if not result:
                return 0.0
            return float(result[0] if isinstance(result, tuple) else result['stock'])
    except Exception as e:
        logger.error(f"Error obteniendo stock: {e}", exc_info=True)
        return 0.0


async def listar_insumos_bajo_stock(conn, umbral_minimo: float = 10.0) -> list[dict]:
    """
    Retorna insumos con stock menor al umbral especificado.
    Por defecto umbral es 10.
    """
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id_insumo, nombre, unidad, stock, activo
                FROM insumo
                WHERE stock < %s AND activo = TRUE
                ORDER BY stock ASC
                """,
                (umbral_minimo,)
            )
            rows = await cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        logger.error(f"Error listando insumos bajo stock: {e}", exc_info=True)
        return []