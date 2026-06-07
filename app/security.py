"""Primitivas de seguridad: hashing de contraseñas y manejo de JWT.

Funciones puras, sin dependencias de FastAPI, para poder testearlas aisladas y
reutilizarlas desde los services. La capa de dependencias vive en
`app/middleware/auth.py`.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# bcrypt es el estándar de facto para contraseñas: lento a propósito y con salt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """Crea un JWT firmado cuyo `sub` identifica al usuario.

    Si no se pasa `expires_delta` se usa el default de la configuración.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Decodifica y valida un JWT. Devuelve el `sub` o None si es inválido/expiró."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        # Firma inválida, token expirado o malformado: tratamos todo como None
        # y dejamos que la capa de dependencias devuelva 401.
        return None
