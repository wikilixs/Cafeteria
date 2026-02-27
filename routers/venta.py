from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import datetime
from decimal import Decimal
from config.enums import EstadoVenta


class Venta(BaseModel):
    id_venta:  int
    id_usuario: int
    fecha:     datetime | None = None
    estado:    EstadoVenta | None = EstadoVenta.PENDIENTE

class VentaInsert(BaseModel):
    id_usuario: int
    estado:    EstadoVenta | None = EstadoVenta.PENDIENTE

router = APIRouter()

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM venta;
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
        SELECT * FROM venta WHERE id_venta = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_venta(venta: VentaInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO venta (id_usuario, estado) 
        VALUES (%s, %s) RETURNING id_venta, id_usuario, fecha, estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (venta.id_usuario, venta.estado))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear la venta")
    
@router.put("/{id}")
async def actualizar_venta(id: int, venta: VentaInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE venta SET id_usuario = %s, estado = %s WHERE id_venta = %s RETURNING id_venta, id_usuario, fecha, estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (venta.id_usuario, venta.estado, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            return resultado
    except Exception as e:
        print(f"Error actualizando venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar la venta")
    
@router.delete("/{id}")
async def eliminar_venta(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM venta WHERE id_venta = %s RETURNING id_venta, id_usuario, fecha, estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            return resultado
    except Exception as e:
        print(f"Error eliminando venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar la venta")
    
