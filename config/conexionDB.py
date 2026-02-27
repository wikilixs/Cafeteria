from fastapi import FastAPI, Depends, HTTPException
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from contextlib import asynccontextmanager

app = FastAPI()

DB_URL = "postgresql://wikilixs:maria-a-comer@localhost:5432/cafeteria"
pool=AsyncConnectionPool(conninfo=DB_URL, open=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await pool.open()
        print("✅ Pool de conexiones abierto exitosamente")
        yield
    finally:
        await pool.close()
        print("🛑 Pool de conexiones cerrado")

async def get_conexion():
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn

app = FastAPI(lifespan=lifespan)

