import logging
from decimal import Decimal
from fastapi import HTTPException
from typing import Optional

logger = logging.getLogger(__name__)


async def registrar_compra(conn, id_proveedor: int | None, id_usuario: int, detalles: list[dict]) -> dict:
    """
    Registra una compra completa y calcula el total automáticamente.

    detalles: lista de dicts con keys:
        id_insumo, cantidad, costo_unitario, fecha_vencimiento (opcional)
    """
    if not detalles:
        raise HTTPException(status_code=400, detail="La compra debe tener al menos un detalle")

    try:
        async with conn.cursor() as cur:

            # 1. Calcular total
            total = sum(
                Decimal(str(d["cantidad"])) * Decimal(str(d["costo_unitario"]))
                for d in detalles
            )
            logger.info(f"Registrando compra — total calculado: {total}")

            # 2. Insertar compra
            await cur.execute(
                """
                INSERT INTO compra (id_proveedor, id_usuario, estado)
                VALUES (%s, %s, 'CONFIRMADA')
                RETURNING id_compra
                """,
                (id_proveedor, id_usuario)
            )
            id_compra_result = await cur.fetchone()
            id_compra = id_compra_result['id_compra']

            # 3. Insertar detalles
            for d in detalles:
                cantidad = Decimal(str(d["cantidad"]))
                await cur.execute(
                    """
                    INSERT INTO detalle_compra
                        (id_compra, id_insumo, cantidad, costo_unitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        id_compra,
                        d["id_insumo"],
                        cantidad,
                        Decimal(str(d["costo_unitario"]))
                    )
                )

            # 4. Registrar movimiento inventario
            for d in detalles:
                await cur.execute(
                    """
                    INSERT INTO movimiento_inventario (tipo, id_insumo, cantidad, signo, referencia_tabla, referencia_id, id_usuario)
                    VALUES ('COMPRA', %s, %s, 1, 'compra', %s, %s)
                    """,
                    (d["id_insumo"], Decimal(str(d["cantidad"])), id_compra, id_usuario)
                )

            await conn.commit()
            logger.info(f"Compra {id_compra} registrada correctamente")
            return {"id_compra": id_compra, "total": total}

    except HTTPException:
        await conn.rollback()
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error registrando compra: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar la compra")


async def obtener_reporte_compras(conn, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, id_proveedor: Optional[int] = None) -> list[dict]:
    """
    Obtiene un reporte de compras con detalles, opcionalmente filtrado por fechas y proveedor.
    """
    consulta = """
        SELECT 
            c.id_compra,
            c.fecha,
            c.estado,
            c.observacion,
            p.nombre AS proveedor,
            u.nombre AS usuario,
            dc.id_insumo,
            i.nombre AS insumo,
            dc.cantidad,
            dc.costo_unitario,
            (dc.cantidad * dc.costo_unitario) AS subtotal
        FROM compra c
        LEFT JOIN proveedor p ON c.id_proveedor = p.id_proveedor
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN detalle_compra dc ON c.id_compra = dc.id_compra
        JOIN insumo i ON dc.id_insumo = i.id_insumo
        WHERE 1=1
    """
    params = []

    if fecha_inicio:
        consulta += " AND c.fecha >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        consulta += " AND c.fecha <= %s"
        params.append(fecha_fin)
    if id_proveedor:
        consulta += " AND c.id_proveedor = %s"
        params.append(id_proveedor)

    consulta += " ORDER BY c.fecha DESC, c.id_compra DESC"

    try:
        async with conn.cursor() as cur:
            await cur.execute(consulta, params)
            cols = [desc[0] for desc in cur.description]
            rows = await cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        logger.error(f"Error obteniendo reporte de compras: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener el reporte de compras")