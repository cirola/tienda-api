"""Fixtures compartidos de pytest.

Levantamos una base SQLite en memoria por test, sobrescribimos la dependencia
`get_db` y construimos un TestClient. También fixtures de usuarios/tokens para
no repetir el setup de auth en cada test.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.user import User, UserRole
from app.rate_limit import limiter
from app.security import create_access_token, hash_password


@pytest.fixture(autouse=True)
def _disable_rate_limit():
    """Desactiva el rate limiting en los tests para evitar 429 espurios."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def db_session():
    """Base SQLite en memoria, aislada por test.

    StaticPool + una sola conexión compartida hace que el ':memory:' persista
    entre la sesión del test y la del request dentro del mismo test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """TestClient con la dependencia get_db apuntando a la base de test."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # el cierre lo maneja el fixture db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Usuarios y tokens ---


@pytest.fixture
def admin_user(db_session) -> User:
    user = User(
        email="admin@test.com",
        full_name="Admin Test",
        hashed_password=hash_password("admin1234"),
        role=UserRole.admin,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session) -> User:
    user = User(
        email="user@test.com",
        full_name="User Test",
        hashed_password=hash_password("user1234"),
        role=UserRole.user,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user) -> dict:
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(normal_user) -> dict:
    token = create_access_token(subject=normal_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def category(db_session) -> Category:
    cat = Category(name="Electrónica", description="Dispositivos")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat
