"""Tests de categorías (CRUD y autorización)."""


def test_listar_categorias_vacio(client):
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    assert resp.json() == []


def test_detalle_categoria(client, category):
    resp = client.get(f"/api/categories/{category.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Electrónica"


def test_detalle_categoria_inexistente(client):
    resp = client.get("/api/categories/9999")
    assert resp.status_code == 404
    assert "error" in resp.json()


def test_crear_categoria_admin(client, admin_headers):
    resp = client.post(
        "/api/categories",
        json={"name": "Hogar", "description": "Cosas de casa"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Hogar"


def test_crear_categoria_user_prohibido(client, user_headers):
    resp = client.post(
        "/api/categories",
        json={"name": "Hogar"},
        headers=user_headers,
    )
    assert resp.status_code == 403


def test_crear_categoria_sin_auth(client):
    resp = client.post("/api/categories", json={"name": "Hogar"})
    assert resp.status_code == 401


def test_crear_categoria_duplicada(client, admin_headers, category):
    resp = client.post(
        "/api/categories",
        json={"name": "Electrónica"},
        headers=admin_headers,
    )
    assert resp.status_code == 409


def test_actualizar_categoria(client, admin_headers, category):
    resp = client.put(
        f"/api/categories/{category.id}",
        json={"description": "Nueva descripción"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Nueva descripción"


def test_eliminar_categoria(client, admin_headers, category):
    resp = client.delete(f"/api/categories/{category.id}", headers=admin_headers)
    assert resp.status_code == 204
    # Ya no existe.
    assert client.get(f"/api/categories/{category.id}").status_code == 404


def test_eliminar_categoria_con_productos(client, admin_headers, category):
    # Creamos un producto en la categoría.
    client.post(
        "/api/products",
        json={"name": "Tele", "price": 100, "stock": 1, "category_id": category.id},
        headers=admin_headers,
    )
    resp = client.delete(f"/api/categories/{category.id}", headers=admin_headers)
    assert resp.status_code == 409
