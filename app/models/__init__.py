"""Reexporta los modelos para que SQLAlchemy registre todas las tablas
con sólo importar el paquete `app.models`.
"""

from app.models.category import Category
from app.models.product import Product
from app.models.user import User

__all__ = ["User", "Product", "Category"]
