from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal

router = APIRouter()

class Insumo(BaseModel):
    id_insumo:     int
    nombre:        str
    categoria:     str | None = None
    unidad_medida: str | None = None
    stock_minimo:  Decimal | None = Decimal("0")
    activo:        bool | None = True

class InsumoInsert(BaseModel):
    nombre:        str
    categoria:     str | None = None
    unidad_medida: str | None = None
    stock_minimo:  Decimal | None = Decimal("0")
    activo:        bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM insumo WHERE id_insumo = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador") 
    
@router.post("/")
async def crear_insumo(insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO insumo (nombre, categoria, unidad_medida, stock_minimo, activo) 
        VALUES (%s, %s, %s, %s, %s) RETURNING id_insumo, nombre, categoria, unidad_medida, stock_minimo, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (insumo.nombre, insumo.categoria, insumo.unidad_medida, insumo.stock_minimo, insumo.activo))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el insumo")
    
@router.put("/{id}")
async def actualizar_insumo(id: int, insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE insumo SET nombre = %s, categoria = %s, unidad_medida = %s, stock_minimo = %s, activo = %s 
        WHERE id_insumo = %s RETURNING id_insumo, nombre, categoria, unidad_medida, stock_minimo, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (insumo.nombre, insumo.categoria, insumo.unidad_medida, insumo.stock_minimo, insumo.activo, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el insumo")
    
@router.delete("/{id}")
async def eliminar_insumo(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM insumo WHERE id_insumo = %s RETURNING id_insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")
            return resultado
    except Exception as e:
        print(f"Error eliminando insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el insumo")
    
