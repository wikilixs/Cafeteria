from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.compra_service import registrar_compra, obtener_reporte_compras
from typing import List, Optional

router = APIRouter()

class Compra(BaseModel):
    id_compra: int
    id_proveedor: int
    id_usuario: int
    fecha: str
    observacion: str

class CompraCreate(BaseModel):
    id_proveedor: int
    id_usuario: int
    fecha: str
    observacion: str | None = None

@router.get("/")
async def listar_compras(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listando compras: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_compra}")
async def obtener_compra(id_compra: int, conn=Depends(get_conexion)):
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
        print(f"Error al obtener compra por ID: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear_compra(compra: CompraCreate, conn=Depends(get_conexion)):
    try:
        compra_id = await registrar_compra(conn, compra)
        return {"id_compra": compra_id, **compra.dict()}
    except Exception as e:
        print(f"Error al registrar compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_compra}")
async def actualizar_compra(id_compra: int, compra: CompraCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE compra
        SET id_proveedor = %s, id_usuario = %s, fecha = %s, observacion = %s
        WHERE id_compra = %s
        RETURNING id_compra, id_proveedor, id_usuario, fecha, observacion;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                consulta,
                (
                    compra.id_proveedor,
                    compra.id_usuario,
                    compra.fecha,
                    compra.observacion,
                    id_compra
                )
            )
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Compra no encontrada")
    except Exception as e:
        print(f"Error al actualizar compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_compra}")
async def eliminar_compra(id_compra: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM compra WHERE id_compra = %s RETURNING id_compra;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_compra,))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"message": "Compra eliminada correctamente"}
            else:
                raise HTTPException(status_code=404, detail="Compra no encontrada")
    except Exception as e:
        print(f"Error al eliminar compra: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
