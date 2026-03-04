import logging
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def registrar_compra(conn, id_proveedor: int | None, id_usuario: int, detalles: list[dict]) -> dict:
    """
    Registra una compra completa y calcula el total automáticamente.

    detalles: lista de dicts con keys:
        id_insumo, cantidad, costo_unitario, fecha_vencimiento (opcional)
    """
    if not detalles:
        raise HTTPException(status_code=400, detail="La compra debe tener al menos un detalle")

    try:
        with conn.cursor() as cur:

            # 1. Calcular total
            total = sum(
                Decimal(str(d["cantidad"])) * Decimal(str(d["costo_unitario"]))
                for d in detalles
            )
            logger.info(f"Registrando compra — total calculado: {total}")

            # 2. Insertar compra
            cur.execute(
                """
                INSERT INTO compra (id_proveedor, id_usuario, total, estado)
                VALUES (%s, %s, %s, 'CONFIRMADA')
                RETURNING id_compra
                """,
                (id_proveedor, id_usuario, total)
            )
            id_compra = cur.fetchone()[0]

            # 3. Insertar detalles — cada fila es un lote
            for d in detalles:
                cantidad = Decimal(str(d["cantidad"]))
                cur.execute(
                    """
                    INSERT INTO detalle_compra
                        (id_compra, id_insumo, cantidad, cantidad_disponible, costo_unitario, fecha_vencimiento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        id_compra,
                        d["id_insumo"],
                        cantidad,
                        cantidad,   # cantidad_disponible = cantidad al inicio
                        Decimal(str(d["costo_unitario"])),
                        d.get("fecha_vencimiento")
                    )
                )

            conn.commit()
            logger.info(f"Compra {id_compra} registrada correctamente")
            return {"id_compra": id_compra, "total": total}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error registrando compra: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar la compra")