from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app

router = APIRouter()

class CategoriaProducto(BaseModel):
    id_categoria_producto: int
    nombre: str

class CategoriaProductoCreate(BaseModel):
    nombre: str

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = "SELECT * FROM categoria_producto"
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
        SELECT * FROM categoria_producto WHERE id_categoria = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.post("/")
async def crear(categoria: CategoriaProductoCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO categoria_producto (nombre) VALUES (%s) RETURNING id_categoria, nombre;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (categoria.nombre,))
            id_categoria_producto = await cursor.fetchone()
            return {"id_categoria_producto": id_categoria_producto[0], "nombre": categoria.nombre}
    except Exception as e:
        print(f"Error creación de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador") 
    
@router.put("/{id}")
async def actualizar(id: int, categoria: CategoriaProductoCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE categoria_producto SET nombre = %s WHERE id_categoria = %s RETURNING id_categoria, nombre;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (categoria.nombre, id))
            resultado = await cursor.fetchone()
            if resultado:
                return {"id_categoria_producto": resultado[0], "nombre": resultado[1]}
            else:
                raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    except Exception as e:
        print(f"Error actualización de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id}")
async def eliminar(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM categoria_producto WHERE id_categoria = %s RETURNING id_categoria;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado:
                return {"message": "Categoría de producto eliminada exitosamente"}
            else:
                raise HTTPException(status_code=404, detail="Categoría de producto no encontrada")
    except Exception as e:
        print(f"Error eliminación de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
