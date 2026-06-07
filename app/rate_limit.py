"""Configuración del rate limiting con slowapi.

Limitamos por IP del cliente. El límite por defecto se aplica globalmente y
endpoints sensibles (login/registro) pueden declarar límites más estrictos con
el decorador `@limiter.limit(...)`.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# key_func define cómo identificar al cliente; por IP es lo más simple para dev.
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
