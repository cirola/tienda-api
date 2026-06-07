"""Carga datos de ejemplo en la base de datos.

Crea las tablas, un usuario admin, un usuario común, algunas categorías y
productos. Es idempotente: si los usuarios ya existen, no los duplica.

Uso:
    python seed.py
"""

from app.database import Base, SessionLocal, engine
from app.models.category import Category
from app.models.product import Product
from app.models.user import User, UserRole
from app.security import hash_password


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # --- Usuarios ---
        if db.query(User).filter(User.email == "admin@tienda.com").first() is None:
            db.add(
                User(
                    email="admin@tienda.com",
                    full_name="Admin Tienda",
                    hashed_password=hash_password("admin1234"),
                    role=UserRole.admin,
                )
            )
        if db.query(User).filter(User.email == "user@tienda.com").first() is None:
            db.add(
                User(
                    email="user@tienda.com",
                    full_name="Usuario Demo",
                    hashed_password=hash_password("user1234"),
                    role=UserRole.user,
                )
            )
        db.commit()

        # --- Categorías ---
        if db.query(Category).count() == 0:
            categorias = {
                "Electrónica": "Dispositivos y accesorios electrónicos",
                "Hogar": "Artículos para el hogar",
                "Libros": "Libros de papel y digitales",
            }
            cat_objs = {
                nombre: Category(name=nombre, description=desc)
                for nombre, desc in categorias.items()
            }
            db.add_all(cat_objs.values())
            db.commit()

            # --- Productos ---
            electronica = cat_objs["Electrónica"]
            hogar = cat_objs["Hogar"]
            libros = cat_objs["Libros"]
            db.add_all(
                [
                    Product(name="Notebook 14\"", description="Intel i5, 16GB RAM",
                            price=799.99, stock=15, category_id=electronica.id),
                    Product(name="Auriculares Bluetooth", description="Cancelación de ruido",
                            price=89.90, stock=50, category_id=electronica.id),
                    Product(name="Cafetera express", description="15 bares de presión",
                            price=129.99, stock=20, category_id=hogar.id),
                    Product(name="Juego de sábanas", description="100% algodón",
                            price=45.50, stock=40, category_id=hogar.id),
                    Product(name="Clean Code", description="Robert C. Martin",
                            price=39.99, stock=30, category_id=libros.id),
                ]
            )
            db.commit()

        print("Seed completado.")
        print("  Admin: admin@tienda.com / admin1234")
        print("  User:  user@tienda.com / user1234")
    finally:
        db.close()


if __name__ == "__main__":
    run()
