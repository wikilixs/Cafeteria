from enum import Enum


class TipoMovInv(str, Enum):
    COMPRA        = "COMPRA"
    VENTA_CONSUMO = "VENTA_CONSUMO"
    AJUSTE        = "AJUSTE"
    MERMA         = "MERMA"
    DEVOLUCION    = "DEVOLUCION"


class EstadoCompra(str, Enum):
    BORRADOR   = "BORRADOR"
    CONFIRMADA = "CONFIRMADA"
    ANULADA    = "ANULADA"


class EstadoVenta(str, Enum):
    EN_PROCESO = "EN_PROCESO"
    PAGADA     = "PAGADA"
    ANULADA    = "ANULADA"


class MetodoPago(str, Enum):
    EFECTIVO = "EFECTIVO"