"""Schemas Pydantic para categorías."""

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Electrónica"])
    description: str | None = Field(
        None, max_length=500, examples=["Dispositivos y accesorios electrónicos"]
    )


class CategoryCreate(CategoryBase):
    """Datos para crear una categoría."""


class CategoryUpdate(BaseModel):
    """Datos para actualizar. Todos los campos son opcionales (PUT parcial)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class CategoryOut(CategoryBase):
    """Representación pública de una categoría."""

    id: int

    model_config = ConfigDict(from_attributes=True)
