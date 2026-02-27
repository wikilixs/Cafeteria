from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app

router = APIRouter()

class Usuario(BaseModel):
    id_usuario:    int
    id_personal:   int
    username:      str
    email:         str
    password_hash: str

class UsuarioInsert(BaseModel):
    id_personal:   int
    username:      str
    email:         str
    password_hash: str
    

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


@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM usuario WHERE id_usuario = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_usuario(usuario: UsuarioInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO usuario (id_personal, username, email, password_hash) 
        VALUES (%s, %s, %s, %s) RETURNING id_usuario, id_personal, username, email, password_hash, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (usuario.id_personal, usuario.username, usuario.email, usuario.password_hash))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando usuario: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el usuario")
    
@router.put("/{id}")
async def actualizar_usuario(id: int, usuario: UsuarioInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE usuario SET id_personal = %s, username = %s, email = %s, password_hash = %s, activo = %s 
        WHERE id_usuario = %s RETURNING id_usuario, id_personal, username, email, password_hash, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (usuario.id_personal, usuario.username, usuario.email, usuario.password_hash, True, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando usuario: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el usuario")
    
@router.delete("/{id}")
async def eliminar_usuario(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM usuario WHERE id_usuario = %s RETURNING id_usuario;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return {"message": "Usuario eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el usuario")

