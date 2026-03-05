from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Proveedor(BaseModel):
    id_proveedor: int
    nombre: str
    telefono: str
    email: str
    nit: str
    activo: bool 

class ProveedorInsert(BaseModel):
    nombre: str
    telefono: str
    email: str
    nit: str
    activo: bool | None = True

class InsumoUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    email: str | None = None
    nit: str | None = None
    activo: bool | None = None

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM proveedor;")
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado proveedor: {e}")
        raise HTTPException(status_code=400, detail="Error al listar proveedores")


@router.post("/")
async def crear_insumo(insumo: ProveedorInsert, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO proveedor 
        (nombre, telefono, email, nit, activo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (
                insumo.nombre,
                insumo.telefono,
                insumo.email,
                insumo.nit,
                insumo.activo
            ))
            return await cursor.fetchone()
    except Exception as e:
        print(f"Error creando proveedor: {e}")
        raise HTTPException(status_code=400, detail="Error al crear proveedor")
    

