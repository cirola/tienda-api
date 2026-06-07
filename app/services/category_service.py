"""Lógica de negocio de categorías (CRUD)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFoundError(f"No existe la categoría con id {category_id}")
    return category


def create_category(db: Session, data: CategoryCreate) -> Category:
    if db.scalar(select(Category).where(Category.name == data.name)):
        raise ConflictError("Ya existe una categoría con ese nombre")
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    updates = data.model_dump(exclude_unset=True)

    # Validar unicidad del nombre sólo si cambió.
    new_name = updates.get("name")
    if new_name and new_name != category.name:
        if db.scalar(select(Category).where(Category.name == new_name)):
            raise ConflictError("Ya existe una categoría con ese nombre")

    for field, value in updates.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    # Regla de negocio: no permitir borrar categorías con productos asociados.
    if category.products:
        raise ConflictError(
            "No se puede eliminar una categoría que tiene productos asociados"
        )
    db.delete(category)
    db.commit()
