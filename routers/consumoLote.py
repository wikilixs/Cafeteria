from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import datetime
from decimal import Decimal

router = APIRouter()

class ConsumoLotes(BaseModel):
    id_consumo:        int
    id_detalle_venta:  int
    id_detalle_compra: int
    cantidad:          Decimal
    fecha:             datetime | None = None

class ConsumoLotesInsert(BaseModel):
    id_detalle_venta:  int
    id_detalle_compra: int
    cantidad:          Decimal

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM consumo_lotes;
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
        SELECT * FROM consumo_lotes WHERE id_consumo = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_consumo_lotes(consumo_lotes: ConsumoLotesInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO consumo_lotes (id_detalle_venta, id_detalle_compra, cantidad) 
        VALUES (%s, %s, %s) RETURNING id_consumo, id_detalle_venta, id_detalle_compra, cantidad, fecha;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (consumo_lotes.id_detalle_venta, consumo_lotes.id_detalle_compra, consumo_lotes.cantidad))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando consumo_lotes: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el consumo_lotes")
    
@router.put("/{id}")
async def actualizar_consumo_lotes(id: int, consumo_lotes: ConsumoLotesInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE consumo_lotes 
        SET id_detalle_venta = %s, id_detalle_compra = %s, cantidad = %s, fecha = NOW() 
        WHERE id_consumo = %s RETURNING id_consumo, id_detalle_venta, id_detalle_compra, cantidad, fecha;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (consumo_lotes.id_detalle_venta, consumo_lotes.id_detalle_compra, consumo_lotes.cantidad, id))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error actualizando consumo_lotes: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el consumo_lotes")
    
@router.delete("/{id}")
async def eliminar_consumo_lotes(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM consumo_lotes WHERE id_consumo = %s RETURNING id_consumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Consumo no encontrado")
            return resultado
    except Exception as e:
        print(f"Error eliminando consumo_lotes: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el consumo_lotes")