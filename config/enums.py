from enum import Enum

class EstadoCompra(str, Enum):
    BORRADOR   = "BORRADOR"
    CONFIRMADA = "CONFIRMADA"
    ANULADA    = "ANULADA"

class EstadoVenta(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADA    = "PAGADA"
    ANULADA   = "ANULADA"