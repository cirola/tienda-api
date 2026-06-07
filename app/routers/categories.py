"""Endpoints de categorías. Lectura pública; escritura sólo admin."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/api/categories", tags=["Categorías"])


@router.get(
    "",
    response_model=list[CategoryOut],
    summary="Listar todas las categorías",
)
def list_categories(db: Session = Depends(get_db)):
    """Devuelve todas las categorías ordenadas por nombre."""
    return category_service.list_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Detalle de una categoría",
    responses={404: {"description": "La categoría no existe"}},
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Devuelve el detalle de una categoría por su id."""
    return category_service.get_category(db, category_id)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría (solo admin)",
    responses={
        201: {"description": "Categoría creada"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        409: {"description": "Ya existe una categoría con ese nombre"},
    },
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Crea una categoría nueva. Requiere token de un usuario admin."""
    return category_service.create_category(db, data)


@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Actualizar una categoría (solo admin)",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "La categoría no existe"},
        409: {"description": "Nombre duplicado"},
    },
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Actualiza los campos enviados de una categoría existente."""
    return category_service.update_category(db, category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría (solo admin)",
    responses={
        204: {"description": "Categoría eliminada"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "La categoría no existe"},
        409: {"description": "Tiene productos asociados"},
    },
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Elimina una categoría sin productos asociados."""
    category_service.delete_category(db, category_id)
