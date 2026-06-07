"""Lógica de negocio de usuarios: registro y autenticación.

Los services reciben una Session y devuelven modelos ORM o lanzan excepciones
de dominio (`app.errors`). No saben nada de HTTP.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ConflictError
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, data: UserCreate, role: UserRole = UserRole.user) -> User:
    """Crea un usuario. Lanza ConflictError si el email ya existe."""
    if get_by_email(db, data.email) is not None:
        raise ConflictError("Ya existe un usuario con ese email")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    """Devuelve el usuario si las credenciales son válidas, si no None."""
    user = get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
