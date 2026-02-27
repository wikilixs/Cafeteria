from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import datetime
from decimal import Decimal
from config.enums import EstadoCompra


router = APIRouter()

class Compra(BaseModel):
    id_compra:    int
    id_proveedor: int | None = None
    id_usuario:   int
    fecha:        datetime | None = None
    total:        Decimal | None = Decimal("0")
    estado:       EstadoCompra | None = EstadoCompra.BORRADOR

class CompraInsert(BaseModel):
    id_proveedor: int | None = None
    id_usuario:   int
    total:        Decimal | None = Decimal("0")
    estado:       EstadoCompra | None = EstadoCompra.BORRADOR

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM compra;
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
        SELECT * FROM compra WHERE id_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_compra(compra: CompraInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO compra (id_proveedor, id_usuario, total, estado) 
        VALUES (%s, %s, %s, %s) RETURNING id_compra, id_proveedor, id_usuario, fecha, total, estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (compra.id_proveedor, compra.id_usuario, compra.total, compra.estado))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear la compra")
    
@router.put("/{id}")
async def actualizar_compra(id: int, compra: CompraInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE compra SET id_proveedor = %s, id_usuario = %s, total = %s, estado = %s 
        WHERE id_compra = %s RETURNING id_compra, id_proveedor, id_usuario, fecha, total, estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (compra.id_proveedor, compra.id_usuario, compra.total, compra.estado, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Compra no encontrada")
            return resultado
    except Exception as e:
        print(f"Error actualizando compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar la compra")
    
@router.delete("/{id}")
async def eliminar_compra(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM compra WHERE id_compra = %s RETURNING id_compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Compra no encontrada")
            return {"message": "Compra eliminada exitosamente"}
    except Exception as e:
        print(f"Error eliminando compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar la compra")