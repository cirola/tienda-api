"""Configuración central de la aplicación.

Carga las variables de entorno (desde el sistema o el archivo .env) y las
expone como un objeto tipado usando pydantic-settings. Centralizar la config
acá evita leer os.environ disperso por todo el código y nos da validación.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Seguridad / JWT ---
    SECRET_KEY: str = "changeme-genera-una-clave-aleatoria-y-larga"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Base de datos ---
    DATABASE_URL: str = "sqlite:///./tienda.db"

    # --- CORS ---
    # Se recibe como string separado por comas y se parsea a lista.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # --- Entorno ---
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Devuelve los orígenes CORS como lista, ignorando entradas vacías."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de Settings.

    Usamos lru_cache para no releer el .env en cada acceso. En los tests se
    puede sobrescribir esta dependencia para inyectar otra configuración.
    """
    return Settings()


settings = get_settings()
