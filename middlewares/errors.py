from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


def add_error_handlers(app):

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error en {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "ok":      False,
                "error":   "Error de validación",
                "detalle": exc.errors()
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning(f"ValueError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "ok":    False,
                "error": str(exc)
            }
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.error(f"Error inesperado en {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "ok":    False,
                "error": "Error interno del servidor"
            }
        )