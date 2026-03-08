from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from datetime import date

router = APIRouter()

class EstadoVenta(BaseModel):
    id_estado: int
    nombre: str

class EstadoVentaCreate(BaseModel):
    nombre: str

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM estado_venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listando estados de venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.get("/{id_estado}")
async def obtener(id_estado: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM estado_venta WHERE id_estado = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_estado,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Estado de venta no encontrado")
    except Exception as e:
        print(f"Error al obtener estado de venta por ID: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.post("/")
async def crear(estado: EstadoVentaCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO estado_venta (nombre) VALUES (%s) RETURNING id_estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (estado.nombre,))
            id_estado = await cursor.fetchone()
            return {"id_estado": id_estado[0], **estado.dict()}
    except Exception as e:
        print(f"Error al crear estado de venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_estado}")
async def actualizar(id_estado: int, estado: EstadoVentaCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE estado_venta SET nombre = %s WHERE id_estado = %s RETURNING id_estado, nombre;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (estado.nombre, id_estado))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Estado de venta no encontrado")
    except Exception as e:
        print(f"Error al actualizar estado de venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_estado}")
async def eliminar(id_estado: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM estado_venta WHERE id_estado = %s RETURNING id_estado;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_estado,))
            resultado = await cursor.fetchone()
            if resultado:
                return {"message": "Estado de venta eliminado"}
            else:
                raise HTTPException(status_code=404, detail="Estado de venta no encontrado")
    except Exception as e:
        print(f"Error al eliminar estado de venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")