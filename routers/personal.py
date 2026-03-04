from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date
from typing import Optional

router = APIRouter()
class Personal(BaseModel):
    id_personal:     int
    id_rol:          int
    ci:              int
    nombres:         str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: date
    telefono:         str
    activo:          bool = True
    fecha_ingreso:   date = date.today()

class PersonalCrear(BaseModel):
    id_rol:          int
    ci:              int
    nombres:         str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: date
    telefono:         str
    activo:          bool = True
    fecha_ingreso:   date = date.today()

class PersonalActualizar(BaseModel):
    id_rol:          Optional[int] = None
    ci:              Optional[int] = None
    nombres:         Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono:         Optional[str] = None
    activo:          Optional[bool] = None
    fecha_ingreso:   Optional[date] = None

@router.get("/")
async def listar_personal(conn=Depends(get_conexion)):
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

@router.post("/")
async def crear_personal(personal: PersonalCrear, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO personal (id_rol, ci, nombres, primer_apellido, segundo_apellido, fecha_nacimiento, telefono, activo, fecha_ingreso) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_personal;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (personal.id_rol, personal.ci, personal.nombres, personal.primer_apellido,
                                            personal.segundo_apellido, personal.fecha_nacimiento,
                                            personal.telefono, personal.activo, personal.fecha_ingreso))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el personal")
    
@router.put("/{id_personal}")
async def actualizar_personal(id_personal: int, personal: PersonalActualizar, conn=Depends(get_conexion)):
    consulta = """
        UPDATE personal SET 
            id_rol = COALESCE(%s, id_rol),
            ci = COALESCE(%s, ci),
            nombres = COALESCE(%s, nombres),
            primer_apellido = COALESCE(%s, primer_apellido),
            segundo_apellido = COALESCE(%s, segundo_apellido),
            fecha_nacimiento = COALESCE(%s, fecha_nacimiento),
            telefono = COALESCE(%s, telefono),
            activo = COALESCE(%s, activo),
            fecha_ingreso = COALESCE(%s, fecha_ingreso)
        WHERE id_personal = %s RETURNING id_personal;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (personal.id_rol, personal.ci, personal.nombres, personal.primer_apellido,
                                            personal.segundo_apellido, personal.fecha_nacimiento,
                                            personal.telefono, personal.activo, personal.fecha_ingreso,
                                            id_personal))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            return resultado
    except Exception as e:
        print(f"Error actualizando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el personal")

@router.delete("/{id_personal}")
async def eliminar_personal(id_personal: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM personal WHERE id_personal = %s RETURNING id_personal;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_personal,))
            resultado = await cursor.fetchone()
            if resultado is None:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            return resultado
    except Exception as e:
        print(f"Error eliminando personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el personal")
    


