from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date

router = APIRouter()

class Personal(BaseModel):
    id_personal:        int
    id_rol:             int
    nombres:            str
    primer_apellido:    str
    segundo_apellido:   str | None = None
    telefono:           str | None = None
    fecha_nacimiento:   date | None = None
    fecha_contratacion: date | None = None
    activo:             bool | None = True

class PersonalInsert(BaseModel):
    id_rol:             int
    nombres:            str
    primer_apellido:    str
    segundo_apellido:   str | None = None
    telefono:           str | None = None
    fecha_nacimiento:   date | None = None
    fecha_contratacion: date | None = None
    activo:             bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM personal;
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
        SELECT * FROM personal WHERE id_personal = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error listado por id de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_personal(personal: PersonalInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO personal (id_rol, nombres, primer_apellido, segundo_apellido, telefono, fecha_nacimiento, fecha_contratacion, activo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_personal, id_rol, nombres, primer_apellido, segundo_apellido, telefono, fecha_nacimiento, fecha_contratacion, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (personal.id_rol, personal.nombres, personal.primer_apellido, personal.segundo_apellido, personal.telefono, personal.fecha_nacimiento, personal.fecha_contratacion, personal.activo))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el personal")

@router.put("/{id}")
async def actualizar_personal(id: int, personal: PersonalInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE personal SET id_rol = %s, nombres = %s, primer_apellido = %s, segundo_apellido = %s, telefono = %s, fecha_nacimiento = %s, fecha_contratacion = %s, activo = %s 
        WHERE id_personal = %s RETURNING id_personal, id_rol, nombres, primer_apellido, segundo_apellido, telefono, fecha_nacimiento, fecha_contratacion, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (personal.id_rol, personal.nombres, personal.primer_apellido, personal.segundo_apellido, personal.telefono, personal.fecha_nacimiento, personal.fecha_contratacion, personal.activo, id))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el personal")
    
@router.delete("/{id}")
async def eliminar_personal(id: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM personal WHERE id_personal = %s RETURNING id_personal;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            return {"message": "Personal eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el personal")

