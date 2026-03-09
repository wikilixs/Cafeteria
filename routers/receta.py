from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion
from datetime import date
from decimal import Decimal

router = APIRouter()


class Receta(BaseModel):
    id_receta: int
    id_producto: int
    id_insumo: int
    cantidad: Decimal

class RecetaInsert(BaseModel):
    id_producto: int
    id_insumo: int
    cantidad: Decimal


# LISTAR TODAS LAS RECETAS
@router.get("/")
async def listar(conn=Depends(get_conexion)):

    consulta = """
        SELECT * FROM receta;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            resultado = await cursor.fetchall()
            return resultado

    except Exception as e:
        print(f"Error listando recetas: {e}")
        raise HTTPException(status_code=400, detail="Error al listar recetas")


# LISTAR POR ID
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):

    consulta = """
        SELECT id_receta, id_producto, id_insumo, cantidad
        FROM receta
        WHERE id_receta = %s;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Receta no encontrada")

            return resultado

    except Exception as e:
        print(f"Error buscando receta: {e}")
        raise HTTPException(status_code=400, detail="Error al buscar receta")


# CREAR RECETA
@router.post("/")
async def crear_receta(receta: RecetaInsert, conn=Depends(get_conexion)):

    consulta = """
        INSERT INTO receta (id_producto, id_insumo, cantidad)
        VALUES (%s, %s, %s)
        RETURNING id_receta, id_producto, id_insumo, cantidad;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(
                consulta,
                (
                    receta.id_producto,
                    receta.id_insumo,
                    receta.cantidad
                )
            )

            resultado = await cursor.fetchone()
            await conn.commit()
            return resultado

    except Exception as e:
        print(f"Error creando receta: {e}")
        raise HTTPException(status_code=400, detail="Error al crear receta")


# ACTUALIZAR RECETA
@router.put("/{id}")
async def actualizar_receta(id: int, receta: RecetaInsert, conn=Depends(get_conexion)):

    consulta = """
        UPDATE receta
        SET id_producto = %s,
            id_insumo = %s,
            cantidad = %s
        WHERE id_receta = %s
        RETURNING id_receta, id_producto, id_insumo, cantidad;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(
                consulta,
                (
                    receta.id_producto,
                    receta.id_insumo,
                    receta.cantidad,
                    id
                )
            )

            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Receta no encontrada")

            await conn.commit()
            return resultado

    except Exception as e:
        print(f"Error actualizando receta: {e}")
        raise HTTPException(status_code=400, detail="Error al actualizar receta")


# ELIMINAR RECETA
@router.delete("/{id}")
async def eliminar_receta(id: int, conn=Depends(get_conexion)):

    consulta = """
        DELETE FROM receta
        WHERE id_receta = %s
        RETURNING id_receta;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Receta no encontrada")

            await conn.commit()
            return {"mensaje": "Receta eliminada correctamente"}

    except Exception as e:
        print(f"Error eliminando receta: {e}")
        raise HTTPException(status_code=400, detail="Error al eliminar receta")