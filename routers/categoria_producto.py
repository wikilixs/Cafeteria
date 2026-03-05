from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()


class CategoriaProducto(BaseModel):
    id_categoria: int
    nombre: str


class CategoriaProductoCreate(BaseModel):
    nombre: str


# LISTAR TODAS LAS CATEGORÍAS
@router.get("/")
async def listar(conn=Depends(get_conexion)):

    consulta = """
        SELECT id_categoria, nombre
        FROM categoria_producto;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            resultado = await cursor.fetchall()
            return resultado

    except Exception as e:
        print(f"Error listando categorías: {e}")
        raise HTTPException(status_code=400, detail="Error al listar categorías")


# LISTAR POR ID
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):

    consulta = """
        SELECT id_categoria, nombre
        FROM categoria_producto
        WHERE id_categoria_producto = %s;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")

            return resultado

    except Exception as e:
        print(f"Error buscando categoría: {e}")
        raise HTTPException(status_code=400, detail="Error al buscar categoría")


# CREAR CATEGORÍA
@router.post("/")
async def crear(categoria: CategoriaProductoCreate, conn=Depends(get_conexion)):

    consulta = """
        INSERT INTO categoria_producto (nombre)
        VALUES (%s)
        RETURNING id_categoria_producto, nombre;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(
                consulta,
                (categoria.nombre,)
            )

            resultado = await cursor.fetchone()
            return resultado

    except Exception as e:
        print(f"Error creando categoría: {e}")
        raise HTTPException(status_code=400, detail="Error al crear categoría")


# ACTUALIZAR CATEGORÍA
@router.put("/{id}")
async def actualizar(id: int, categoria: CategoriaProductoCreate, conn=Depends(get_conexion)):

    consulta = """
        UPDATE categoria_producto
        SET nombre = %s
        WHERE id_categoria_producto = %s
        RETURNING id_categoria_producto, nombre;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(
                consulta,
                (categoria.nombre, id)
            )

            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")

            return resultado

    except Exception as e:
        print(f"Error actualizando categoría: {e}")
        raise HTTPException(status_code=400, detail="Error al actualizar categoría")


# ELIMINAR CATEGORÍA
@router.delete("/{id}")
async def eliminar(id: int, conn=Depends(get_conexion)):

    consulta = """
        DELETE FROM categoria_producto
        WHERE id_categoria_producto = %s
        RETURNING id_categoria_producto;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")

            return {"mensaje": "Categoría eliminada correctamente"}

    except Exception as e:
        print(f"Error eliminando categoría: {e}")
        raise HTTPException(status_code=400, detail="Error al eliminar categoría")