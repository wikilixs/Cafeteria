from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal

class ProductoInsumo(BaseModel):
    id_producto_insumo: int
    id_producto:        int
    id_insumo:          int
    cantidad:           Decimal

class ProductoInsumoInsert(BaseModel):
    id_producto: int
    id_insumo:   int
    cantidad:    Decimal

router = APIRouter()

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM producto_insumo;
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
        SELECT * FROM producto_insumo WHERE id_producto_insumo = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_producto_insumo(producto_insumo: ProductoInsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO producto_insumo (id_producto, id_insumo, cantidad) 
        VALUES (%s, %s, %s) RETURNING id_producto_insumo, id_producto, id_insumo, cantidad;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (producto_insumo.id_producto, producto_insumo.id_insumo, producto_insumo.cantidad))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando producto_insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el producto_insumo")
    
@router.put("/{id}")
async def actualizar_producto_insumo(id: int, producto_insumo: ProductoInsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE producto_insumo SET id_producto = %s, id_insumo = %s, cantidad = %s 
        WHERE id_producto_insumo = %s RETURNING id_producto_insumo, id_producto, id_insumo, cantidad;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (producto_insumo.id_producto, producto_insumo.id_insumo, producto_insumo.cantidad, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="ProductoInsumo no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando producto_insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el producto_insumo")
    
@router.delete("/{id}")
async def eliminar_producto_insumo(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM producto_insumo WHERE id_producto_insumo = %s RETURNING id_producto_insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="ProductoInsumo no encontrado")
            return resultado
    except Exception as e:
        print(f"Error eliminando producto_insumo: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el producto_insumo")
    
