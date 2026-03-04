from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date

router = APIRouter()

class DetalleCompra(BaseModel):
    id_detalle_compra: int
    id_compra: int
    id_insumo: int
    cantidad: float
    costo_unitario: float

class DetalleCompraCreate(BaseModel):
    id_compra: int
    id_insumo: int
    cantidad: float
    costo_unitario: float

class DetalleCompraUpdate(BaseModel):
    id_compra: int = None
    id_insumo: int = None
    cantidad: float = None
    costo_unitario: float = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM detalle_compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.get("/{id_detalle_compra}")
async def obtener(id_detalle_compra: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM detalle_compra WHERE id_detalle_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_detalle_compra,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Detalle de compra no encontrado")
    except Exception as e:
        print(f"Error al obtener detalle de compra por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
