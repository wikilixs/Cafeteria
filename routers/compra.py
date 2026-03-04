from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app

router = APIRouter()

class Compra(BaseModel):
    id_compra: int
    id_proveedor: int
    fecha: str
    estado: str
    observacion: str

class CompraCreate(BaseModel):
    id_proveedor: int
    fecha: str
    estado: str
    observacion: str

class CompraUpdate(BaseModel):
    id_proveedor: int = None
    fecha: str = None
    estado: str = None
    observacion: str = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_compra}")
async def obtener(id_compra: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM compra WHERE id_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_compra,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Compra no encontrada")
    except Exception as e:
        print(f"Error al obtener compra por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(compra: CompraCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO compra (id_proveedor, fecha, estado, observacion)
        VALUES (%s, %s, %s, %s) RETURNING id_compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (compra.id_proveedor, compra.fecha, compra.estado, compra.observacion))
            id_compra = await cursor.fetchone()
            await conn.commit()
            return {"id_compra": id_compra[0]}
    except Exception as e:
        print(f"Error al crear compra en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_compra}")
async def actualizar(id_compra: int, compra: CompraUpdate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE compra SET id_proveedor = COALESCE(%s, id_proveedor),
                         fecha = COALESCE(%s, fecha),
                         estado = COALESCE(%s, estado),
                         observacion = COALESCE(%s, observacion)
        WHERE id_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (compra.id_proveedor, compra.fecha, compra.estado, compra.observacion, id_compra))
            await conn.commit()
            return {"message": "Compra actualizada exitosamente"}
    except Exception as e:
        print(f"Error al actualizar compra en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_compra}")
async def eliminar(id_compra: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM compra WHERE id_compra = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_compra,))
            await conn.commit()
            return {"message": "Compra eliminada exitosamente"}
    except Exception as e:
        print(f"Error al eliminar compra en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
