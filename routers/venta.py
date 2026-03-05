from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.venta_service import registrar_venta, obtener_reporte_ventas
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from schema.enums import EstadoVenta


router = APIRouter()


class VentaRespuesta(BaseModel):
    id_venta:       int
    id_usuario:     int
    fecha:          datetime
    estado:         EstadoVenta
    total:          Decimal
    nota:           str

class DetalleVentaInput(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float

class VentaCreate(BaseModel):
    id_usuario: int
    detalles: List[DetalleVentaInput]

class VentaUpdate(BaseModel):
    id_usuario:     Optional[int] = None
    fecha:          Optional[datetime] = None
    estado:         Optional[EstadoVenta] = None
    total:          Optional[Decimal] = None
    nota:           Optional[str] = None


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
        print(f"Error listado gral de Psycopg: {e}")
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
        print(f"Error al obtener venta por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(venta: VentaCreate, conn=Depends(get_conexion)):
    try:
        detalles = [d.dict() for d in venta.detalles]
        result = await registrar_venta(conn, venta.id_usuario, detalles)
        return result
    except Exception as e:
        print(f"Error al crear venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al crear la venta")

@router.put("/{id_venta}")
async def actualizar(id_venta: int, venta: VentaUpdate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE venta SET id_usuario = COALESCE(%s, id_usuario),
                         fecha = COALESCE(%s, fecha),
                         estado = COALESCE(%s, estado),
                         total = COALESCE(%s, total),
                         nota = COALESCE(%s, nota)
        WHERE id_venta = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                venta.id_usuario,
                venta.fecha,
                venta.estado.value if venta.estado else None,
                venta.total,
                venta.nota,
                id_venta
            ))
            await conn.commit()
            return {"message": "Venta actualizada exitosamente"}
    except Exception as e:
        print(f"Error al actualizar venta en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_venta}")
async def eliminar(id_venta: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM venta WHERE id_venta = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_venta,))
            await conn.commit()
            return {"message": "Venta eliminada exitosamente"}
    except Exception as e:
        print(f"Error al eliminar venta en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

@router.get("/reporte")
async def reporte_ventas(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    id_usuario: Optional[int] = None,
    conn=Depends(get_conexion)
):
    try:
        return await obtener_reporte_ventas(conn, fecha_inicio, fecha_fin, id_usuario)
    except Exception as e:
        print(f"Error al obtener reporte de ventas: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener el reporte")
