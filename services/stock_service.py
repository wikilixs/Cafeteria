import logging
logger = logging.getLogger(__name__)


def verificar_stock_minimos(conn) -> list[dict]:
    """Retorna insumos bajo stock mínimo."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                i.id_insumo,
                i.nombre,
                i.categoria,
                i.unidad_medida,
                i.stock_minimo,
                COALESCE(SUM(dc.cantidad_disponible), 0) AS stock_actual
            FROM insumo i
            LEFT JOIN detalle_compra dc ON dc.id_insumo = i.id_insumo
            WHERE i.activo = TRUE
            GROUP BY i.id_insumo, i.nombre, i.categoria, i.unidad_medida, i.stock_minimo
            HAVING COALESCE(SUM(dc.cantidad_disponible), 0) < i.stock_minimo
            ORDER BY stock_actual ASC
        """)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]


def obtener_stock_insumo(conn, id_insumo: int) -> float:
    """Retorna el stock actual de un insumo."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(SUM(cantidad_disponible), 0)
            FROM detalle_compra
            WHERE id_insumo = %s
        """, (id_insumo,))
        return float(cur.fetchone()[0])