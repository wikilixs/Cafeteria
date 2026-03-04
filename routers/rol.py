from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date
from typing import Optional, List

router = APIRouter()

class Rol(BaseModel):
    id_rol: int
    nombre: str

class RolCreate(BaseModel):
    nombre: str

class RolUpdate(BaseModel):
    nombre: Optional[str] = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM rol;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.post("/")
async def crear_rol(rol: RolCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO rol (nombre) 
        VALUES (%s) RETURNING id_rol, nombre;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (rol.nombre,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando rol: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el rol")
    

@router.put("/{id_rol}")
async def actualizar_rol(id_rol: int, rol: RolUpdate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE rol SET nombre = COALESCE(%s, nombre) 
        WHERE id_rol = %s RETURNING id_rol, nombre;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (rol.nombre, id_rol))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando rol: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el rol")
    
