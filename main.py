from fastapi import FastAPI, Depends, HTTPException
from config.conexionDB import pool, get_conexion, app
from routers import rol,personal, usuario
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




def main():
    print("Hello from cafeteria!")


if __name__ == "__main__":
    main()

