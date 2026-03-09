from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Cliente(BaseModel):
    id_cliente: int
    nombre: str
    nit: str 
    activo : bool | None = True

class ClienteCreate(BaseModel):
    nombre: str
    nit: str 
    activo : bool | None = True

@router.get("/")
async def listar(conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM cliente;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado gral de Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    

@router.get("/buscar")
async def buscar_cliente(q: str = "", conn=Depends(get_conexion)):
    """
    Busca clientes por NIT/CI o nombre (búsqueda parcial, case-insensitive).
    Devuelve máximo 10 resultados.
    """
    consulta = """
        SELECT id_cliente, nombre, nit
        FROM cliente
        WHERE activo = TRUE
          AND (nit ILIKE %s OR nombre ILIKE %s)
        ORDER BY nombre
        LIMIT 10;
    """
    try:
        patron = f"%{q}%"
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (patron, patron))
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error al buscar cliente: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al buscar clientes")

@router.get("/{id_cliente}")
async def obtener(id_cliente: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT * FROM cliente WHERE id_cliente = %s;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_cliente,))
            resultado = await cursor.fetchone()
            if resultado:
                return resultado
            else:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        print(f"Error al obtener cliente por ID en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.post("/")
async def crear(cliente: ClienteCreate, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO cliente (nombre, nit, activo) VALUES (%s, %s, %s) RETURNING id_cliente;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (cliente.nombre, cliente.nit, cliente.activo))
            id_cliente = await cursor.fetchone()
            await conn.commit()
            return {"id_cliente": id_cliente[0], **cliente.dict()}
    except Exception as e:
        print(f"Error al crear cliente en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.put("/{id_cliente}")
async def actualizar(id_cliente: int, cliente: ClienteCreate, conn=Depends(get_conexion)):
    consulta = """
        UPDATE cliente SET nombre = %s, nit = %s, activo = %s WHERE id_cliente = %s RETURNING id_cliente;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (cliente.nombre, cliente.nit, cliente.activo, id_cliente))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"id_cliente": resultado[0], **cliente.dict()}
            else:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        print(f"Error al actualizar cliente en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")
    
@router.delete("/{id_cliente}")
async def eliminar(id_cliente: int, conn=Depends(get_conexion)):
    consulta = """
        DELETE FROM cliente WHERE id_cliente = %s RETURNING id_cliente;
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_cliente,))
            resultado = await cursor.fetchone()
            if resultado:
                await conn.commit()
                return {"id_cliente": resultado[0], "message": "Cliente eliminado exitosamente"}
            else:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        print(f"Error al eliminar cliente en Psycopg: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error, consulte con su Administrador")



