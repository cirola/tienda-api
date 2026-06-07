"""Lógica de negocio de productos: CRUD, paginación, filtros, orden y búsqueda."""

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

# Campos permitidos para ordenar. Lista blanca para evitar inyección por el
# parámetro `sort_by` (nunca interpolamos input del usuario como columna).
_SORTABLE_FIELDS = {
    "name": Product.name,
    "price": Product.price,
    "stock": Product.stock,
    "created_at": Product.created_at,
}


def _ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise NotFoundError(f"No existe la categoría con id {category_id}")


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise NotFoundError(f"No existe el producto con id {product_id}")
    return product


def list_products(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 20,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[list[Product], int]:
    """Lista productos con filtros, orden y paginación.

    Devuelve (items, total) donde `total` es la cantidad antes de paginar, para
    que el router pueda calcular la cantidad de páginas.
    """
    stmt = select(Product)

    # --- Filtros ---
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # --- Total (sobre el query filtrado, sin orden ni paginación) ---
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    # --- Orden (con lista blanca) ---
    column = _SORTABLE_FIELDS.get(sort_by, Product.created_at)
    direction = asc if order == "asc" else desc
    stmt = stmt.order_by(direction(column))

    # --- Paginación ---
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    items = list(db.scalars(stmt))
    return items, total


def search_products(db: Session, q: str) -> list[Product]:
    """Busca productos cuyo nombre contenga `q` (case-insensitive)."""
    stmt = select(Product).where(Product.name.ilike(f"%{q}%")).order_by(Product.name)
    return list(db.scalars(stmt))


def create_product(db: Session, data: ProductCreate) -> Product:
    _ensure_category_exists(db, data.category_id)
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    updates = data.model_dump(exclude_unset=True)

    if "category_id" in updates:
        _ensure_category_exists(db, updates["category_id"])

    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
