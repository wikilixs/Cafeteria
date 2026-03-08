from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from services.venta_service import registrar_venta
from datetime import date
from typing import List, Optional
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

class DetalleVenta(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float

class VentaRegistro(BaseModel):
    id_usuario: int
    id_cliente: Optional[int] = None       # Si es None se crea el cliente
    nombre_cliente: Optional[str] = None   # Requerido si id_cliente es None
    nit_cliente: Optional[str] = None      # Opcional (NIT/CI para factura)
    id_estado: int
    metodo_pago: str
    detalles: List[DetalleVenta]

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


@router.post("/")
async def crear_venta(venta: VentaRegistro, conn=Depends(get_conexion)):
    """
    Registra una venta con detalles de productos.
    Body: {
      "id_usuario": 1,
      "id_cliente": 2,
      "id_estado": 1,
      "metodo_pago": "EFECTIVO",
      "detalles": [
        {"id_producto": 1, "cantidad": 2, "precio_unitario": 25.00}
      ]
    }
    """
    try:
        detalles_dict = [d.dict() for d in venta.detalles]
        resultado = await registrar_venta(
            conn,
            venta.id_usuario,
            venta.id_cliente,
            venta.id_estado,
            venta.metodo_pago,
            detalles_dict,
            nombre_cliente=venta.nombre_cliente,
            nit_cliente=venta.nit_cliente,
        )
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al registrar venta: {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error, consulte con su Administrador")


@router.put("/{id_venta}")
async def actualizar_venta(id_venta: int, venta: VentaCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE venta
        SET id_usuario = %s, id_cliente = %s, id_estado = %s, metodo_pago = %s
        WHERE id_venta = %s
        RETURNING id_venta, id_usuario, id_cliente, id_estado, metodo_pago, fecha;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                consulta,
                (
                    venta.id_usuario,
                    venta.id_cliente,
                    venta.id_estado,
                    venta.metodo_pago,
                    id_venta
                )
            )
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
    except Exception as e:
        print(f"Error al actualizar venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.delete("/{id_venta}")
async def eliminar_venta(id_venta: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM venta WHERE id_venta = %s RETURNING id_venta;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_venta,))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"message": "Venta eliminada correctamente"}
            else:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
    except Exception as e:
        print(f"Error al eliminar venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")