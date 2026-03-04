from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from typing import Optional
from decimal import Decimal
from datetime import datetime
from schema.enums import TipoMovInv

router = APIRouter()

class MovimientoInventario(BaseModel):
    id_movimiento:    int
    tipo:             str
    id_insumo:        int
    fecha:            datetime
    cantidad:         Decimal
    signo:            int
    referencia_tabla: str
    referencia_id:    int
    id_usuario:       int
    nota:             str

class MovimientoInventarioCreate(BaseModel):
    tipo:             TipoMovInv
    id_insumo:        int
    fecha:            datetime
    cantidad:         Decimal
    referencia_tabla: str
    referencia_id:    int
    id_usuario:       int
    nota:             str

class MovimientoInventarioUpdate(BaseModel):
    tipo:             Optional[TipoMovInv] = None
    id_insumo:        Optional[int] = None
    fecha:            Optional[datetime] = None
    cantidad:         Optional[Decimal] = None
    referencia_tabla: Optional[str] = None
    referencia_id:    Optional[int] = None
    id_usuario:       Optional[int] = None
    nota:             Optional[str] = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM movimiento_inventario;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.get("/{id_movimiento}")
async def obtener(id_movimiento: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM movimiento_inventario WHERE id_movimiento = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_movimiento,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Movimiento de Inventario no encontrado")
    except Exception as e:
        print(f"Error al obtener movimiento de inventario por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(movimiento: MovimientoInventarioCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO movimiento_inventario (tipo, id_insumo, fecha, cantidad, signo, referencia_tabla, referencia_id, id_usuario, nota)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_movimiento;
    """
    signo = 1 if movimiento.tipo == TipoMovInv.ENTRADA else -1
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                movimiento.tipo.value,
                movimiento.id_insumo,
                movimiento.fecha,
                movimiento.cantidad,
                signo,
                movimiento.referencia_tabla,
                movimiento.referencia_id,
                movimiento.id_usuario,
                movimiento.nota
            ))
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"id_movimiento": nuevo_id[0]}
    except Exception as e:
        print(f"Error al crear movimiento de inventario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_movimiento}")
async def actualizar(id_movimiento: int, movimiento: MovimientoInventarioUpdate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE movimiento_inventario
        SET tipo = COALESCE(%s, tipo),
            id_insumo = COALESCE(%s, id_insumo),
            fecha = COALESCE(%s, fecha),
            cantidad = COALESCE(%s, cantidad),
            referencia_tabla = COALESCE(%s, referencia_tabla),
            referencia_id = COALESCE(%s, referencia_id),
            id_usuario = COALESCE(%s, id_usuario),
            nota = COALESCE(%s, nota)
        WHERE id_movimiento = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                movimiento.tipo.value if movimiento.tipo else None,
                movimiento.id_insumo,
                movimiento.fecha,
                movimiento.cantidad,
                movimiento.referencia_tabla,
                movimiento.referencia_id,
                movimiento.id_usuario,
                movimiento.nota,
                id_movimiento
            ))
            await conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Movimiento de Inventario no encontrado")
            return {"message": "Movimiento de Inventario actualizado exitosamente"}
    except Exception as e:
        print(f"Error al actualizar movimiento de inventario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

@router.delete("/{id_movimiento}")
async def eliminar(id_movimiento: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM movimiento_inventario WHERE id_movimiento = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_movimiento,))
            await conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Movimiento de Inventario no encontrado")
            return {"message": "Movimiento de Inventario eliminado exitosamente"}
    except Exception as e:
        print(f"Error al eliminar movimiento de inventario en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
