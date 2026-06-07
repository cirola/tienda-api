"""Schemas Pydantic para productos, incluyendo la respuesta paginada."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryOut


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Notebook 14\""])
    description: str | None = Field(None, examples=["Intel i5, 16GB RAM, 512GB SSD"])
    # gt=0: el precio debe ser positivo. ge=0 en stock: no puede ser negativo.
    price: float = Field(..., gt=0, examples=[799.99])
    stock: int = Field(0, ge=0, examples=[25])
    category_id: int = Field(..., gt=0, examples=[1])


class ProductCreate(ProductBase):
    """Datos para crear un producto."""


class ProductUpdate(BaseModel):
    """Datos para actualizar. Todos los campos opcionales."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_id: int | None = Field(None, gt=0)


class ProductOut(ProductBase):
    """Representación pública de un producto, con su categoría embebida."""

    id: int
    created_at: datetime
    category: CategoryOut

    model_config = ConfigDict(from_attributes=True)


# --- Paginación genérica ---
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envoltorio de respuesta paginada reutilizable.

    Incluye metadatos (`total`, `page`, `per_page`, `pages`) además de los
    items, para que el cliente pueda construir su paginador.
    """

    items: list[T]
    total: int = Field(..., examples=[42])
    page: int = Field(..., examples=[1])
    per_page: int = Field(..., examples=[20])
    pages: int = Field(..., examples=[3])

    model_config = ConfigDict(from_attributes=True)
