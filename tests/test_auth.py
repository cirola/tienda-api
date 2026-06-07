"""Tests de autenticación y autorización."""

from datetime import timedelta

from app.security import create_access_token


def test_register_ok(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "nuevo@test.com", "full_name": "Nuevo", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "nuevo@test.com"
    assert data["role"] == "user"
    assert "password" not in data and "hashed_password" not in data


def test_register_email_duplicado(client, normal_user):
    resp = client.post(
        "/api/auth/register",
        json={"email": normal_user.email, "full_name": "Otro", "password": "password123"},
    )
    assert resp.status_code == 409


def test_register_password_corta(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "x@test.com", "full_name": "X", "password": "123"},
    )
    assert resp.status_code == 422


def test_login_ok(client, normal_user):
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "user1234"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_credenciales_invalidas(client, normal_user):
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "incorrecta"},
    )
    assert resp.status_code == 401


def test_me_con_token(client, user_headers):
    resp = client.get("/api/auth/me", headers=user_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@test.com"


def test_me_sin_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_token_expirado(client, normal_user):
    # Token con expiración en el pasado.
    expired = create_access_token(
        subject=normal_user.id, expires_delta=timedelta(minutes=-1)
    )
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401


def test_me_token_invalido(client):
    resp = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer token-falso"}
    )
    assert resp.status_code == 401
