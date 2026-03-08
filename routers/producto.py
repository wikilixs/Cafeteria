from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion
from decimal import Decimal

router = APIRouter()


class Producto(BaseModel):
    id_producto: int
    id_categoria: int
    nombre: str
    costo: Decimal
    precio_venta: Decimal
    activo: bool

class ProductoInsert(BaseModel):
    id_categoria: int
    nombre: str
    costo: Decimal
    precio_venta: Decimal
    activo: bool | None = True


# LISTAR TODOS
@router.get("/")
async def listar(conn=Depends(get_conexion)):

    consulta = """
        SELECT * 
        FROM producto;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            resultado = await cursor.fetchall()
            return resultado

    except Exception as e:
        print(f"Error listando productos: {e}")
        raise HTTPException(status_code=400, detail="Error al listar productos")


# LISTAR POR ID
@router.get("/{id}")
async def listar_por_id(id: int, conn=Depends(get_conexion)):

    consulta = """
        SELECT id_producto, id_categoria, nombre, costo, precio_venta, activo
        FROM producto
        WHERE id_producto = %s;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            return resultado

    except Exception as e:
        print(f"Error buscando producto: {e}")
        raise HTTPException(status_code=400, detail="Error al buscar producto")


# CREAR PRODUCTO
@router.post("/")
async def crear_producto(producto: ProductoInsert, conn=Depends(get_conexion)):

    consulta = """
        INSERT INTO producto
        (id_categoria, nombre, costo, precio_venta, activo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_producto, id_categoria, nombre, costo, precio_venta, activo;
    """

    try:
        async with conn.cursor() as cursor:
 
            await cursor.execute(
                consulta,
                (
                    producto.id_categoria,
                    producto.nombre,
                    producto.costo,
                    producto.precio_venta,
                    producto.activo
                )
            )


            resultado = await cursor.fetchone()
            return resultado

    except Exception as e:
        print(f"Error creando producto: {e}")
        raise HTTPException(status_code=400, detail="Error al crear producto")


# ACTUALIZAR PRODUCTO
@router.put("/{id}")
async def actualizar_producto(id: int, producto: ProductoInsert, conn=Depends(get_conexion)):

    consulta = """
        UPDATE producto
        SET nombre = %s, costo = %s, costo = %s, precio_venta = %s, activo = %s
        WHERE id_producto = %s
        RETURNING id_producto, id_categoria, nombre, costo, precio_venta, activo;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(
                consulta,
                (
                    producto.nombre,
                    producto.costo,
                    producto.precio_venta,
                    producto.activo
                )
            )

            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            return resultado

    except Exception as e:
        print(f"Error actualizando producto: {e}")
        raise HTTPException(status_code=400, detail="Error al actualizar producto")


# ELIMINAR PRODUCTO
@router.delete("/{id}")
async def eliminar_producto(id: int, conn=Depends(get_conexion)):

    consulta = """
        DELETE FROM producto
        WHERE id_producto = %s
        RETURNING id_producto;
    """

    try:
        async with conn.cursor() as cursor:

            await cursor.execute(consulta, (id,))
            resultado = await cursor.fetchone()

            if resultado is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            return {"mensaje": "Producto eliminado correctamente"}

    except Exception as e:
        print(f"Error eliminando producto: {e}")
        raise HTTPException(status_code=400, detail="Error al eliminar producto")

