from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date


router = APIRouter()

from typing import Optional


class Usuario(BaseModel):
    id_usuario: int
    id_personal: int
    username:    str
    email:       str
    password:    str

class UsuarioCreate(BaseModel):
    id_personal: int
    username:    str
    email:       str
    password:    str

class UsuarioUpdate(BaseModel):
    id_personal: Optional[int] = None
    username:    Optional[str] = None
    email:       Optional[str] = None
    password:    Optional[str] = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM usuario;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.get("/{id_usuario}")
async def obtener(id_usuario: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM usuario WHERE id_usuario = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_usuario,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        print(f"Error al obtener usuario por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

