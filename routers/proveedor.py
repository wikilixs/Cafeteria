from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app

router = APIRouter()

class Proveedor(BaseModel):
    id_proveedor: int
    nombre:       str
    contacto:     str | None = None
    telefono:     str | None = None
    email:        str | None = None
    direccion:    str | None = None
    activo:       bool | None = True

class ProveedorInsert(BaseModel):
    nombre:   str
    contacto: str | None = None
    telefono: str | None = None
    email:    str | None = None
    direccion: str | None = None
    activo:   bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM proveedor;
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
        SELECT * FROM proveedor WHERE id_proveedor = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_proveedor(proveedor: ProveedorInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO proveedor (nombre, contacto, telefono, email, direccion, activo) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_proveedor, nombre, contacto, telefono, email, direccion, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (proveedor.nombre, proveedor.contacto, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando proveedor: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el proveedor")
    
@router.put("/{id}")
async def actualizar_proveedor(id: int, proveedor: ProveedorInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE proveedor SET nombre = %s, contacto = %s, telefono = %s, email = %s, direccion = %s, activo = %s 
        WHERE id_proveedor = %s RETURNING id_proveedor, nombre, contacto, telefono, email, direccion, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (proveedor.nombre, proveedor.contacto, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando proveedor: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el proveedor")
    
@router.delete("/{id}")
async def eliminar_proveedor(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM proveedor WHERE id_proveedor = %s RETURNING id_proveedor;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            return {"message": "Proveedor eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando proveedor: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el proveedor")