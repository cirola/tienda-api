"""Endpoints de productos. Lectura pública; escritura sólo admin.

Incluye listado con paginación/filtros/orden y búsqueda por nombre.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.schemas.product import Page, ProductCreate, ProductOut, ProductUpdate
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Productos"])


@router.get(
    "",
    response_model=Page[ProductOut],
    summary="Listar productos (paginado, con filtros y orden)",
)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Ítems por página (máx. 100)"),
    category_id: int | None = Query(None, gt=0, description="Filtrar por categoría"),
    min_price: float | None = Query(None, ge=0, description="Precio mínimo"),
    max_price: float | None = Query(None, ge=0, description="Precio máximo"),
    sort_by: str = Query(
        "created_at",
        pattern="^(name|price|stock|created_at)$",
        description="Campo de ordenamiento",
    ),
    order: str = Query("desc", pattern="^(asc|desc)$", description="asc o desc"),
):
    """Lista productos con paginación.

    Ejemplo: `/api/products?page=1&per_page=20&category_id=1&min_price=10&max_price=100&sort_by=price&order=asc`
    """
    items, total = product_service.list_products(
        db,
        page=page,
        per_page=per_page,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )
    pages = (total + per_page - 1) // per_page  # ceil division
    return Page(items=items, total=total, page=page, per_page=per_page, pages=pages)


@router.get(
    "/search",
    response_model=list[ProductOut],
    summary="Buscar productos por nombre",
)
def search_products(
    q: str = Query(..., min_length=1, description="Texto a buscar en el nombre"),
    db: Session = Depends(get_db),
):
    """Busca productos cuyo nombre contenga `q` (case-insensitive).

    Ejemplo: `/api/products/search?q=notebook`
    """
    return product_service.search_products(db, q)


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Detalle de un producto",
    responses={404: {"description": "El producto no existe"}},
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Devuelve el detalle de un producto por su id."""
    return product_service.get_product(db, product_id)


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un producto (solo admin)",
    responses={
        201: {"description": "Producto creado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "La categoría indicada no existe"},
    },
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Crea un producto asociado a una categoría existente."""
    return product_service.create_product(db, data)


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    summary="Actualizar un producto (solo admin)",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "Producto o categoría inexistente"},
    },
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Actualiza los campos enviados de un producto existente."""
    return product_service.update_product(db, product_id, data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto (solo admin)",
    responses={
        204: {"description": "Producto eliminado"},
        401: {"description": "No autenticado"},
        403: {"description": "Requiere rol admin"},
        404: {"description": "El producto no existe"},
    },
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Elimina un producto por su id."""
    product_service.delete_product(db, product_id)
