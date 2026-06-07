"""Endpoints de autenticación: registro, login y perfil."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.rate_limit import limiter
from app.schemas.user import Token, UserCreate, UserLogin, UserOut
from app.security import create_access_token
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    responses={
        201: {"description": "Usuario creado correctamente"},
        409: {"description": "El email ya está registrado"},
        422: {"description": "Datos inválidos"},
    },
)
@limiter.limit("5/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    """Registra un usuario nuevo con rol `user`.

    - **email**: debe ser único y con formato válido.
    - **password**: mínimo 8 caracteres (se guarda hasheada).
    """
    user = user_service.register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión y obtener un JWT",
    responses={
        200: {"description": "Login exitoso, devuelve el access token"},
        401: {"description": "Email o contraseña incorrectos"},
    },
)
@limiter.limit("10/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """Valida las credenciales y devuelve un JWT tipo Bearer.

    Ejemplo de respuesta:
    ```json
    {"access_token": "eyJhbGciOi...", "token_type": "bearer"}
    ```
    """
    user = user_service.authenticate(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Perfil del usuario autenticado",
    responses={
        200: {"description": "Datos del usuario logueado"},
        401: {"description": "Token ausente, inválido o expirado"},
    },
)
def me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario asociado al token enviado."""
    return current_user
