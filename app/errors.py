"""Excepciones de dominio y handlers para respuestas de error consistentes.

Los services lanzan estas excepciones agnósticas de HTTP; los routers las dejan
propagar y los handlers registrados en `main.py` las traducen a JSON con la
forma estándar: {"error": {"code": <int>, "message": <str>}}.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Error de dominio con un status HTTP asociado."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    """Violación de una regla de unicidad o de negocio (409)."""

    status_code = status.HTTP_409_CONFLICT


def _error_body(code: int, message: str) -> dict:
    """Construye el cuerpo JSON estándar de error."""
    return {"error": {"code": code, "message": message}}


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, exc.message),
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, exc.detail),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    # Aplanamos los errores de Pydantic a un mensaje legible manteniendo el
    # detalle estructurado en `details`.
    details = exc.errors()
    message = "Error de validación en los datos enviados"
    body = _error_body(status.HTTP_422_UNPROCESSABLE_ENTITY, message)
    body["error"]["details"] = details
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body
    )


def register_error_handlers(app) -> None:
    """Registra todos los handlers en la app FastAPI."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
