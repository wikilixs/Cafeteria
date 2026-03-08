from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal
from typing import Optional

router = APIRouter()

class DetalleVentaCrear(BaseModel):
    id_detalle_venta: int
    id_venta:        int
    id_producto:     int
    cantidad:        int
    precio_unitario: Decimal

class DetalleVentaActualizar(BaseModel):
    id_venta:        int
    id_producto:     int
    cantidad:        int
    precio_unitario: Decimal

class DetalleVentaActualizar(BaseModel):
    cantidad:        Optional[int]     = None
    precio_unitario: Optional[Decimal] = None


@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM detalle_venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_detalle_venta}")
async def obtener(id_detalle_venta: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM detalle_venta WHERE id_detalle_venta = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_detalle_venta,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
    except Exception as e:
        print(f"Error al obtener detalle de venta por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(detalle_venta: DetalleVentaCrear, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s) RETURNING id_detalle_venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (detalle_venta.id_venta, detalle_venta.id_producto, detalle_venta.cantidad, detalle_venta.precio_unitario))
            id_detalle_venta = await cursor.fetchone()
            await conn.commit()
            return {"id_detalle_venta": id_detalle_venta[0]}
    except Exception as e:
        print(f"Error al crear detalle de venta en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_detalle_venta}")
async def actualizar(id_detalle_venta: int, detalle_venta: DetalleVentaActualizar, conn=Depends(get_conexion)):
    consulta = """
        UPDATE detalle_venta
        SET cantidad = COALESCE(%s, cantidad), precio_unitario = COALESCE(%s, precio_unitario)
        WHERE id_detalle_venta = %s
        RETURNING id_detalle_venta, id_venta, id_producto, cantidad, precio_unitario;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (detalle_venta.cantidad, detalle_venta.precio_unitario, id_detalle_venta))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
    except Exception as e:
        print(f"Error al actualizar detalle de venta en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_detalle_venta}")
async def eliminar(id_detalle_venta: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM detalle_venta WHERE id_detalle_venta = %s RETURNING id_detalle_venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_detalle_venta,))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"id_detalle_venta": resultado[0]}
            else:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
    except Exception as e:
        print(f"Error al eliminar detalle de venta en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
