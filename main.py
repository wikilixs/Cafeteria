from fastapi import FastAPI, Depends, HTTPException
from config.conexionDB import pool, get_conexion, app
from routers import rol, personal, usuario, insumo, producto, productoInsumo, proveedor, compra, detalleCompra
from routers import venta


app.include_router(rol.router, prefix="/rol")
app.include_router(personal.router, prefix="/personal")
app.include_router(usuario.router, prefix="/usuario")
app.include_router(insumo.router, prefix="/insumo")
app.include_router(producto.router, prefix="/producto")
app.include_router(productoInsumo.router, prefix="/producto_insumo")
app.include_router(proveedor.router, prefix="/proveedor")
app.include_router(compra.router, prefix="/compra")
app.include_router(detalleCompra.router, prefix="/detalle_compra")
app.include_router(venta.router, prefix="/venta")


def main():
    print("Hello from cafeteria!")


if __name__ == "__main__":
    main()
