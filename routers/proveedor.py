from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Proveedor(BaseModel):
    id_proveedor: int
    nombre: str
    telefono: int
    email: str
    direccion: str
    activo: bool

class ProveedorCreate(BaseModel):
    nombre: str
    telefono: int
    email: str
    direccion: str
    activo: bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM proveedor;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

@router.get("/{id_proveedor}")
async def obtener(id_proveedor: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM proveedor WHERE id_proveedor = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_proveedor,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    except Exception as e:
        print(f"Error al obtener proveedor por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.post("/")
async def crear(proveedor: ProveedorCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO proveedor (nombre, telefono, email, direccion, activo) VALUES (%s, %s, %s, %s, %s) RETURNING id_proveedor;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (proveedor.nombre, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo))
            id_proveedor = await cursor.fetchone()
            await conn.commit()
            return {"id_proveedor": id_proveedor[0], **proveedor.dict()}
    except Exception as e:
        print(f"Error al crear proveedor en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")


@router.put("/{id_proveedor}")
async def actualizar(id_proveedor: int, proveedor: ProveedorCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE proveedor
        SET nombre = %s, telefono = %s, email = %s, direccion = %s, activo = %s
        WHERE id_proveedor = %s
        RETURNING id_proveedor, nombre, telefono, email, direccion, activo;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (proveedor.nombre, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo, id_proveedor))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    except Exception as e:
        print(f"Error al actualizar proveedor en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")

  

