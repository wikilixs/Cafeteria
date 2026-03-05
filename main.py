from fastapi import FastAPI, Depends, HTTPException
from config.conexionDB import pool, get_conexion, app
from routers import rol,personal, usuario, detalle_compra, compra, detalle_venta, movimiento_inventario, venta, categoria_producto, producto, proveedor, insumo, receta
from middlewares.corps import add_cors
from middlewares.errors import add_error_handlers
from middlewares.login import setup_logging
import os, logging

os.makedirs("logs", exist_ok=True)
setup_logging()

add_cors(app)
add_error_handlers(app)


app.include_router(rol.router, prefix="/rol")
app.include_router(personal.router, prefix="/personal")
app.include_router(usuario.router, prefix="/usuario")
app.include_router(detalle_compra.router, prefix="/detalle_compra")
app.include_router(compra.router, prefix="/compra")
app.include_router(detalle_venta.router, prefix="/detalle_venta")
app.include_router(movimiento_inventario.router, prefix="/movimiento_inventario")
app.include_router(venta.router, prefix="/venta")
app.include_router(categoria_producto.router, prefix="/categoria_producto")
app.include_router(producto.router, prefix="/producto")
app.include_router(insumo.router, prefix="/insumo")
app.include_router(proveedor.router, prefix="/proveedor")
app.include_router(receta.router, prefix="/receta")


def main():
    print("Hello from cafeteria!")


if __name__ == "__main__":
    main()

