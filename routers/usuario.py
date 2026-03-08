from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.creacion_empleado import crear_usuario_para_empleado
from datetime import date

    
router = APIRouter()

from typing import Optional


class Usuario(BaseModel):
    id_usuario: int
    id_personal: int
    email:       str
    password:    str
    activo:      bool

class UsuarioCreate(BaseModel):
    id_personal: int
    username:    str
    email:       str
    password:    str
    activo:      bool | None = True

class UsuarioCreateAuto(BaseModel):
    id_personal: int


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

@router.post("/")
async def crear(usuario: UsuarioCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO usuario (id_personal, email, password_hash, activo)
        VALUES (%s, %s, %s, %s) RETURNING id_usuario;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (usuario.id_personal, usuario.email, usuario.password, usuario.activo))
            id_usuario = await cursor.fetchone()
            await conn.commit()
            return {"id_usuario": id_usuario[0]}
    except Exception as e:
        print(f"Error al crear usuario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.post("/crear")
async def crear_usuario_autogenerado(data: UsuarioCreateAuto, conn=Depends(get_conexion)):
    """
    Crea un usuario autogenerando email y contraseña (últimos 6 dígitos del CI).
    Body: {"id_personal": 1}
    """
    try:
        resultado = await crear_usuario_para_empleado(conn, data.id_personal)
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al crear usuario")

@router.put("/{id_usuario}")
async def actualizar(id_usuario: int, usuario: UsuarioCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE usuario
        SET id_personal = %s, email = %s, password_hash = %s, activo = %s
        WHERE id_usuario = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (usuario.id_personal, usuario.email, usuario.password, usuario.activo, id_usuario))
            await conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return {"message": "Usuario actualizado correctamente"}
    except Exception as e:
        print(f"Error al actualizar usuario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_usuario}")
async def eliminar(id_usuario: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM usuario WHERE id_usuario = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_usuario,))
            await conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return {"message": "Usuario eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar usuario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

