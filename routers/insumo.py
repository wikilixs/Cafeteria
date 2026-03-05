from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion
from decimal import Decimal

router = APIRouter()

class Insumo(BaseModel):
    id_insumo: int
    nombre: str
    unidad: str | None = None
    stock_actual : float | None = None
    stock_minimo: Decimal | None = Decimal("0")
    stock_maximo: float | None = None
    activo: bool | None = True


class InsumoInsert(BaseModel):
    nombre: str
    unidad: str | None = None
    stock_actual : float | None = None
    stock_minimo: Decimal | None = Decimal("0")
    stock_maximo: float | None = None
    activo: bool | None = True

# LISTAR TODOS
@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT *
        FROM insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de insumos: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


# LISTAR POR ID
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_insumo, nombre, unidad, stock_actual, stock_minimo, stock_maximo, activo
        FROM insumo
        WHERE id_insumo = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")

            return resultado
    except Exception as e:
        print(f"Error listado por id: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


# CREAR INSUMO
@router.post("/")
async def crear_insumo(insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO insumo (nombre, unidad, stock_actual, stock_minimo, stock_maximo, activo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_insumo, id_insumo, nombre, unidad, stock_actual, stock_minimo, stock_maximo, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                consulta,
                (
                    insumo.nombre,
                    insumo.categoria,
                    insumo.unidad_medida,
                    insumo.stock_minimo,
                    insumo.activo
                )
            )
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el insumo")


# ACTUALIZAR INSUMO
@router.put("/{id}")
async def actualizar_insumo(id: int, insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE insumo
        SET    nombre %s, 
    unidad %s,
    stock_actual %s,
    stock_minimo %s,
    stock_maximo %s, 
    activo %s
        WHERE id_insumo = %s
        RETURNING id_insumo, id_insumo, nombre, unidad, stock_actual, stock_minimo, stock_maximo, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                consulta,
                (
                    insumo.nombre,
                    insumo.categoria,
                    insumo.unidad_medida,
                    insumo.stock_minimo,
                    insumo.activo,
                    id
                )
            )

            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")

            return resultado
    except Exception as e:
        print(f"Error actualizando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el insumo")


# ELIMINAR INSUMO
@router.delete("/{id}")
async def eliminar_insumo(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM insumo
        WHERE id_insumo = %s
        RETURNING id_insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")

            return {"mensaje": "Insumo eliminado correctamente"}
    except Exception as e:
        print(f"Error eliminando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el insumo")