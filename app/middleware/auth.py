"""Dependencias de autenticación y autorización.

`get_current_user` resuelve el usuario a partir del Bearer token; `require_admin`
lo restringe a administradores. Se usan con Depends() en los routers.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.security import decode_access_token

# HTTPBearer hace que el botón "Authorize" de Swagger muestre un único campo
# donde pegás el token. auto_error=False para devolver 401 (no 403) si falta.
bearer_scheme = HTTPBearer(auto_error=False)

# Excepción reutilizable para credenciales inválidas (401).
_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Devuelve el usuario autenticado o lanza 401.

    Cubre token ausente, inválido, expirado o que apunta a un usuario borrado.
    """
    if credentials is None:
        raise _credentials_exception

    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise _credentials_exception

    user = db.get(User, int(subject)) if subject.isdigit() else None
    if user is None:
        raise _credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Permite el acceso sólo a administradores; si no, 403."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return current_user
