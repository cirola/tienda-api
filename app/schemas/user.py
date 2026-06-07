"""Schemas Pydantic para usuarios y autenticación.

Separamos los schemas de entrada (lo que acepta la API) de los de salida (lo
que devuelve) para nunca exponer el hash de la contraseña.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(..., examples=["ana@example.com"])
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Ana García"])


class UserCreate(UserBase):
    """Datos para registrar un usuario."""

    password: str = Field(..., min_length=8, max_length=128, examples=["password123"])


class UserOut(UserBase):
    """Representación pública de un usuario (sin contraseña)."""

    id: int
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Credenciales de login."""

    email: EmailStr = Field(..., examples=["ana@example.com"])
    password: str = Field(..., examples=["password123"])


class Token(BaseModel):
    """Respuesta del login: el JWT y su tipo."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Contenido decodificado del JWT (claim `sub` = id de usuario)."""

    sub: str | None = None
