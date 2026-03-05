from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Insumo(BaseModel):
    id_insumo: int
    nombre: str
    descripcion: str | None = None
    stock: float
    unidad_medida: str
    id_proveedor: int
    activo: bool | None = True

class InsumoInsert(BaseModel):
    nombre: str
    descripcion: str | None = None
    stock: float
    unidad_medida: str
    id_proveedor: int
    activo: bool | None = True


@router.get("/")
async def listar(conn=Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM insumo;")
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado insumo: {e}")
        raise HTTPException(status_code=400, detail="Error al listar insumos")


@router.post("/")
async def crear_insumo(insumo: InsumoInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO insumo 
        (nombre, descripcion, stock, unidad_medida, id_proveedor, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                insumo.nombre,
                insumo.descripcion,
                insumo.stock,
                insumo.unidad_medida,
                insumo.id_proveedor,
                insumo.activo
            ))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando insumo: {e}")
        raise HTTPException(status_code=400, detail="Error al crear insumo")