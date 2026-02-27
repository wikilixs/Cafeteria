from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal

router = APIRouter()


class Producto(BaseModel):
    id_producto:   int
    nombre:        str
    descripcion:   str | None = None
    unidad_medida: str | None = None
    precio_venta:  Decimal | None = Decimal("0")
    activo:        bool | None = True

class ProductoInsert(BaseModel):
    nombre:        str
    descripcion:   str | None = None
    unidad_medida: str | None = None
    precio_venta:  Decimal | None = Decimal("0")
    activo:        bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM producto;
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
        SELECT * FROM producto WHERE id_producto = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_producto(producto: ProductoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO producto (nombre, descripcion, unidad_medida, precio_venta, activo) 
        VALUES (%s, %s, %s, %s, %s) RETURNING id_producto, nombre, descripcion, unidad_medida, precio_venta, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (producto.nombre, producto.descripcion, producto.unidad_medida, producto.precio_venta, producto.activo))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando producto: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el producto")
    
@router.put("/{id}")
async def actualizar_producto(id: int, producto: ProductoInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE producto SET nombre = %s, descripcion = %s, unidad_medida = %s, precio_venta = %s, activo = %s 
        WHERE id_producto = %s RETURNING id_producto, nombre, descripcion, unidad_medida, precio_venta, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (producto.nombre, producto.descripcion, producto.unidad_medida, producto.precio_venta, producto.activo, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando producto: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el producto")
    
@router.delete("/{id}")
async def eliminar_producto(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM producto WHERE id_producto = %s RETURNING id_producto;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return {"message": "Producto eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando producto: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el producto")
    
