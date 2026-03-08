from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from config.conexionDB import pool, get_conexion, app
from routers import categoria_producto, producto, insumo, proveedor, personal, usuario, rol, compra, detalle_compra, venta, detalle_venta, receta, cliente, estado_venta
from routers import auth
from middlewares.corps import add_cors
from middlewares.errors import add_error_handlers
from middlewares.login import setup_logging
import os, logging

os.makedirs("logs", exist_ok=True)
setup_logging()

add_cors(app)
add_error_handlers(app)

# Ruta raíz redirige al login
@app.get("/")
async def root():
    return RedirectResponse(url="/app/index.html")

app.include_router(auth.router, prefix="/auth", tags=["auth"])


app.include_router(rol.router, prefix="/rol")
app.include_router(personal.router, prefix="/personal")
app.include_router(usuario.router, prefix="/usuario")
app.include_router(cliente.router, prefix="/cliente")
app.include_router(detalle_compra.router, prefix="/detalle_compra")
app.include_router(compra.router, prefix="/compra")
app.include_router(detalle_venta.router, prefix="/detalle_venta")
app.include_router(venta.router, prefix="/venta")
app.include_router(categoria_producto.router, prefix="/categoria_producto")
app.include_router(producto.router, prefix="/producto")
app.include_router(insumo.router, prefix="/insumo")
app.include_router(proveedor.router, prefix="/proveedor")
app.include_router(receta.router, prefix="/receta")
app.include_router(estado_venta.router, prefix="/estado_venta")




def main():
    print("Hello from cafeteria!")


if __name__ == "__main__":
    main()


# ---- Servir frontend (debe ir al final, después de todos los routers) ----
app.mount("/app", StaticFiles(directory="fontend", html=True), name="frontend")
