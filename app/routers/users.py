"""Endpoints de gestión de usuarios (sólo admin).

El perfil propio vive en /api/auth/me; acá exponemos el listado administrativo.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/users", tags=["Usuarios"])


@router.get(
    "",
    response_model=list[UserOut],
    summary="Listar todos los usuarios (solo admin)",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
    },
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Devuelve todos los usuarios registrados. Sólo para administradores."""
    return list(db.scalars(select(User).order_by(User.id)))
