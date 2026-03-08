from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion
from decimal import Decimal

router = APIRouter()

class Insumo(BaseModel):
    id_insumo: int
    nombre: str
    unidad: str
    stock : float
    activo: bool 

class InsumoInsert(BaseModel):
    nombre: str
    unidad: str
    stock : float
    activo: bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_insumo}")
async def obtener(id_insumo: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM insumo WHERE id_insumo = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_insumo,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")
    except Exception as e:
        print(f"Error al obtener insumo por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO insumo (nombre, unidad, stock, activo) VALUES (%s, %s, %s, %s) RETURNING id_insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (insumo.nombre, insumo.unidad, insumo.stock, insumo.activo))
            id_insumo = await cursor.fetchone()
            await conn.commit()
            return {"id_insumo": id_insumo[0], **insumo.dict()}
    except Exception as e:
        print(f"Error al crear insumo en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

@router.put("/{id_insumo}")
async def actualizar(id_insumo: int, insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        UPDATE insumo
        SET nombre = %s, unidad = %s, stock = %s, activo = %s
        WHERE id_insumo = %s
        RETURNING id_insumo, nombre, unidad, stock, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                consulta,
                (
                    insumo.nombre,
                    insumo.unidad,
                    insumo.stock,
                    insumo.activo,
                    id_insumo
                )
            )
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")
    except Exception as e:
        print(f"Error al actualizar insumo en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.delete("/{id_insumo}")
async def eliminar(id_insumo: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM insumo WHERE id_insumo = %s RETURNING id_insumo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_insumo,))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"message": "Insumo eliminado correctamente"}
            else:
                raise HTTPException(status_code=404, detail="Insumo no encontrado")
    except Exception as e:
        print(f"Error al eliminar insumo en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

