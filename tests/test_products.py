"""Tests de productos: CRUD, autorización, paginación, filtros y búsqueda."""

import pytest


@pytest.fixture
def producto(client, admin_headers, category):
    """Crea un producto base y devuelve su JSON."""
    resp = client.post(
        "/api/products",
        json={
            "name": "Notebook",
            "description": "i5 16GB",
            "price": 800.0,
            "stock": 10,
            "category_id": category.id,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    return resp.json()


def test_crear_producto_admin(producto):
    assert producto["name"] == "Notebook"
    assert producto["category"]["name"] == "Electrónica"


def test_crear_producto_user_prohibido(client, user_headers, category):
    resp = client.post(
        "/api/products",
        json={"name": "X", "price": 10, "category_id": category.id},
        headers=user_headers,
    )
    assert resp.status_code == 403


def test_crear_producto_categoria_inexistente(client, admin_headers):
    resp = client.post(
        "/api/products",
        json={"name": "X", "price": 10, "category_id": 9999},
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_crear_producto_precio_invalido(client, admin_headers, category):
    resp = client.post(
        "/api/products",
        json={"name": "X", "price": -5, "category_id": category.id},
        headers=admin_headers,
    )
    assert resp.status_code == 422


def test_detalle_producto(client, producto):
    resp = client.get(f"/api/products/{producto['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == producto["id"]


def test_detalle_producto_inexistente(client):
    resp = client.get("/api/products/9999")
    assert resp.status_code == 404


def test_listar_productos_paginado(client, producto):
    resp = client.get("/api/products?page=1&per_page=20")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["pages"] == 1
    assert len(body["items"]) == 1


def test_filtrar_por_precio(client, admin_headers, category, producto):
    # producto cuesta 800. Filtramos un rango que lo excluye.
    resp = client.get("/api/products?min_price=1000&max_price=2000")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_filtrar_por_categoria(client, producto, category):
    resp = client.get(f"/api/products?category_id={category.id}")
    assert resp.json()["total"] == 1
    resp_vacio = client.get("/api/products?category_id=9999")
    assert resp_vacio.json()["total"] == 0


def test_ordenar_por_precio(client, admin_headers, category):
    for nombre, precio in [("Barato", 10.0), ("Caro", 500.0), ("Medio", 100.0)]:
        client.post(
            "/api/products",
            json={"name": nombre, "price": precio, "category_id": category.id},
            headers=admin_headers,
        )
    resp = client.get("/api/products?sort_by=price&order=asc")
    precios = [p["price"] for p in resp.json()["items"]]
    assert precios == sorted(precios)


def test_buscar_por_nombre(client, producto):
    resp = client.get("/api/products/search?q=note")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert client.get("/api/products/search?q=zzzz").json() == []


def test_actualizar_producto(client, admin_headers, producto):
    resp = client.put(
        f"/api/products/{producto['id']}",
        json={"price": 999.99},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == 999.99


def test_eliminar_producto(client, admin_headers, producto):
    resp = client.delete(f"/api/products/{producto['id']}", headers=admin_headers)
    assert resp.status_code == 204
    assert client.get(f"/api/products/{producto['id']}").status_code == 404


def test_eliminar_producto_user_prohibido(client, user_headers, producto):
    resp = client.delete(f"/api/products/{producto['id']}", headers=user_headers)
    assert resp.status_code == 403
