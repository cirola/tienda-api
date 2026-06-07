"""Configuración de SQLAlchemy: engine, sesión y base declarativa.

Expone `get_db`, la dependencia que inyecta una sesión por request y la
cierra al terminar. Todos los modelos heredan de `Base`.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite necesita `check_same_thread=False` porque FastAPI puede usar la
# conexión desde distintos threads del pool. Para otras bases este connect_args
# queda vacío.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa de la que heredan todos los modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: provee una sesión y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
