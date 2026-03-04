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
    
