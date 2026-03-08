from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.creacion_empleado import crear_empleado
from datetime import date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class Personal(BaseModel):
    id_personal: int 
    id_rol : int
    ci: int
    nombres: str
    primer_apellido: str
    segundo_apellido: str
    fecha_nacimiento: date
    telefono: int
    activo : bool | None = True
    fecha_ingreso: date

class PersonalCreate(BaseModel):
    id_rol : int
    ci: int
    nombres: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[int] = None
    fecha_ingreso: date
    activo: Optional[bool] = True

class PersonalCreateSimple(BaseModel):
    id_rol: int
    ci: int
    nombres: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[int] = None
    fecha_ingreso: date
    crear_usuario: bool = False


@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT 
            p.*,
            r.nombre as rol_nombre
        FROM personal p
        LEFT JOIN rol r ON p.id_rol = r.id_rol;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.get("/{id_personal}")
async def obtener_personal(id_personal: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM personal WHERE id_personal = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_personal,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
    except Exception as e:
        print(f"Error al obtener personal por ID: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.post("/crear")
async def crear_personal_simple(personal: PersonalCreateSimple, conn=Depends(get_conexion)):
    """
    Crea un empleado (personal) con opción de crear usuario automáticamente.
    Si crear_usuario=true, genera email y contraseña automáticamente.
    """
    try:
        resultado = await crear_empleado(
            conn,
            personal.id_rol,
            personal.ci,
            personal.nombres,
            personal.primer_apellido,
            personal.segundo_apellido,
            personal.fecha_nacimiento,
            personal.telefono,
            personal.fecha_ingreso,
            crear_usuario=personal.crear_usuario
        )
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al crear personal: {e}")
        raise HTTPException(status_code=500, detail="Error al crear personal")
@router.post("/")
async def crear_personal(personal: PersonalCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO personal (id_rol, ci, nombres, primer_apellido, segundo_apellido, fecha_nacimiento, telefono, fecha_ingreso)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_personal;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                personal.id_rol,
                personal.ci,
                personal.nombres,
                personal.primer_apellido,
                personal.segundo_apellido,
                personal.fecha_nacimiento,
                personal.telefono,
                personal.fecha_ingreso
            ))
            id_personal = await cursor.fetchone()
            await conn.commit()
            return {"id_personal": id_personal[0]}
    except Exception as e:
        print(f"Error al crear personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear el personal")
    

@router.put("/{id_personal}")
async def actualizar_personal(id_personal: int, personal: PersonalCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE personal SET id_rol = %s, ci = %s, nombres = %s, primer_apellido = %s, segundo_apellido = %s, fecha_nacimiento = %s, telefono = %s, fecha_ingreso = %s, activo = %s
        WHERE id_personal = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                personal.id_rol,
                personal.ci,
                personal.nombres,
                personal.primer_apellido,
                personal.segundo_apellido,
                personal.fecha_nacimiento,
                personal.telefono,
                personal.fecha_ingreso,
                personal.activo,
                id_personal
            ))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            await conn.commit()
            return {"detail": "Personal actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar personal: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Ocurrió un error al actualizar el personal")



@router.delete("/{id_personal}")
async def eliminar_personal(id_personal: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM personal WHERE id_personal = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_personal,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Personal no encontrado")
            await conn.commit()
            return {"detail": "Personal eliminado exitosamente"}
    except Exception as e:
        print(f"Error al eliminar personal: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al eliminar el personal")
    
