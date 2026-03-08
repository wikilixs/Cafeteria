from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config.conexionDB import pool, get_conexion, app
from decimal import Decimal

router = APIRouter()

class DetalleCompra(BaseModel):
    id_detalle_compra: int
    id_compra: int
    id_insumo: int
    catidad: float
    costo_unitario: Decimal

