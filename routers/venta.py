from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.venta_service import registrar_venta, obtener_reporte_ventas
from datetime import date
from schema.enums import EstadoVenta


router = APIRouter()


class VentaRespuesta(BaseModel):
    id_venta: int
    id_usuario: int
    id_cliente: int
    id_estado: int
    metodo_pago: str
    fecha: date
    
class VentaCreate(BaseModel):
    id_usuario: int
    id_cliente: int
    id_estado: int
    metodo_pago: str
    fecha: date 

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listando ventas: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_venta}")
async def obtener(id_venta: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM venta WHERE id_venta = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_venta,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
    except Exception as e:
        print(f"Error al obtener venta por ID: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    




