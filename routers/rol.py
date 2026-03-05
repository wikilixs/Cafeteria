from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()


class Rol(BaseModel):
    id_rol: int
    nombre: str


class RolInsert(BaseModel):
    nombre: str


# LISTAR TODOS
@router.get("/")
async def listar(conn=Depends(get_conexion)):

    consulta = """
        SELECT id_rol, nombre
        FROM rol;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            resultado = await cursor.fetchall()
            return resultado

    except Exception as e:
        print(f"Error listando roles: {e}")
        raise HTTPException(status_code=400, detail="Error al listar roles")


# LISTAR POR ID
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):

    consulta = """
        SELECT id_rol, nombre
        FROM rol
        WHERE id_rol = %s;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Rol no encontrado")

            return resultado

    except Exception as e:
        print(f"Error buscando rol: {e}")
        raise HTTPException(status_code=400, detail="Error al buscar rol")


# CREAR ROL
@router.post("/")
async def crear_rol(rol: RolInsert, conn=Depends(get_conexion)):

    consulta = """
        INSERT INTO rol (nombre)
        VALUES (%s)
        RETURNING id_rol, nombre;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (rol.nombre,))
            resultado = await cursor.fetchone()

            return resultado

    except Exception as e:
        print(f"Error creando rol: {e}")
        raise HTTPException(status_code=400, detail="Error al crear rol")


# ACTUALIZAR ROL
@router.put("/{id}")
async def actualizar_rol(id: int, rol: RolInsert, conn=Depends(get_conexion)):

    consulta = """
        UPDATE rol
        SET nombre = %s
        WHERE id_rol = %s
        RETURNING id_rol, nombre;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (rol.nombre, id))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Rol no encontrado")

            return resultado

    except Exception as e:
        print(f"Error actualizando rol: {e}")
        raise HTTPException(status_code=400, detail="Error al actualizar rol")


# ELIMINAR ROL
@router.delete("/{id}")
async def eliminar_rol(id: int, conn=Depends(get_conexion)):

    consulta = """
        DELETE FROM rol
        WHERE id_rol = %s
        RETURNING id_rol;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Rol no encontrado")

            return {"mensaje": "Rol eliminado correctamente"}

    except Exception as e:
        print(f"Error eliminando rol: {e}")
        raise HTTPException(status_code=400, detail="Error al eliminar rol")