"""Modelo de categoría."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Una categoría tiene muchos productos. No usamos cascade delete para no
    # borrar productos silenciosamente: el service valida que esté vacía.
    products: Mapped[list["Product"]] = relationship(
        back_populates="category", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - sólo debug
        return f"<Category id={self.id} name={self.name!r}>"
