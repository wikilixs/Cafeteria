from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal
from datetime import date

router = APIRouter()

class DetalleCompra(BaseModel):
    id_detalle_compra:   int
    id_compra:           int
    id_insumo:           int
    cantidad:            Decimal
    cantidad_disponible: Decimal
    costo_unitario:      Decimal
    fecha_vencimiento:   date | None = None

class DetalleCompraInsert(BaseModel):
    id_compra:           int
    id_insumo:           int
    cantidad:            Decimal
    cantidad_disponible: Decimal
    costo_unitario:      Decimal
    fecha_vencimiento:   date | None = None

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
    
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM detalle_compra WHERE id_detalle_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

@router.post("/")
async def crear_detalle_compra(detalle_compra: DetalleCompraInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO detalle_compra (id_compra, id_insumo, cantidad, cantidad_disponible, costo_unitario, fecha_vencimiento) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_detalle_compra, id_compra, id_insumo, cantidad, cantidad_disponible, costo_unitario, fecha_vencimiento;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (detalle_compra.id_compra, detalle_compra.id_insumo, detalle_compra.cantidad, detalle_compra.cantidad_disponible, detalle_compra.costo_unitario, detalle_compra.fecha_vencimiento))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando detalle_compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el detalle de compra")
    
@router.put("/{id}")
async def actualizar_detalle_compra(id: int, detalle_compra: DetalleCompraInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE detalle_compra SET id_compra = %s, id_insumo = %s, cantidad = %s, cantidad_disponible = %s, costo_unitario = %s, fecha_vencimiento = %s 
        WHERE id_detalle_compra = %s RETURNING id_detalle_compra, id_compra, id_insumo, cantidad, cantidad_disponible, costo_unitario, fecha_vencimiento;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (detalle_compra.id_compra, detalle_compra.id_insumo, detalle_compra.cantidad, detalle_compra.cantidad_disponible, detalle_compra.costo_unitario, detalle_compra.fecha_vencimiento, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Detalle de compra no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando detalle_compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el detalle de compra")
    

@router.delete("/{id}")
async def eliminar_detalle_compra(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM detalle_compra WHERE id_detalle_compra = %s RETURNING id_detalle_compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Detalle de compra no encontrado")
            return {"message": "Detalle de compra eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando detalle_compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el detalle de compra")
    
