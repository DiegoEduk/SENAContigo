from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class SENAContigoException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(SENAContigoException):
    def __init__(self, resource_name: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} con id '{resource_id}' no fue encontrado."
        )


class UnauthorizedException(SENAContigoException):
    def __init__(self, detail: str = "No autenticado o token inválido"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(SENAContigoException):
    def __init__(self, detail: str = "No tiene permisos para realizar esta acción"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class DuplicateResourceException(SENAContigoException):
    def __init__(self, detail: str = "El recurso ya existe"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error": exc.detail if isinstance(exc.detail, str) else "Error en la solicitud",
            "details": exc.detail if not isinstance(exc.detail, str) else None,
            "path": str(request.url.path)
        },
        headers=exc.headers
    )
