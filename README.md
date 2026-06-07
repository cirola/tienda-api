# Tienda API

API REST de una tienda online construida con **FastAPI**. Incluye autenticación
con JWT, roles de usuario, CRUD de categorías y productos con paginación,
filtros, ordenamiento y búsqueda, rate limiting, CORS y manejo de errores
consistente en JSON.

## Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy 2.0** (ORM) sobre **SQLite** (desarrollo local)
- **Pydantic v2** para validación y serialización
- **JWT** (python-jose) + **bcrypt** (passlib) para auth
- **slowapi** para rate limiting
- **pytest** + **httpx** para tests

## Estructura

```
app/
  main.py            # App FastAPI: CORS, rate limit, logging, handlers, routers
  config.py          # Settings con pydantic-settings (lee .env)
  database.py        # Engine, sesión y dependencia get_db
  security.py        # Hashing de contraseñas y creación/validación de JWT
  errors.py          # Excepciones de dominio + handlers JSON consistentes
  rate_limit.py      # Limiter compartido de slowapi
  models/            # Modelos SQLAlchemy (user, product, category)
  schemas/           # Schemas Pydantic (entrada/salida)
  routers/           # Endpoints (auth, users, products, categories)
  services/          # Lógica de negocio (sin saber de HTTP)
  middleware/auth.py # Dependencias get_current_user / require_admin
tests/               # conftest + tests por recurso
seed.py              # Datos de ejemplo
```

## Instalación y ejecución

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# editá .env y poné un SECRET_KEY propio (openssl rand -hex 32)

# 4. (Opcional) Cargar datos de ejemplo
python seed.py

# 5. Levantar el servidor
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000`.

### Documentación interactiva (Swagger)

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Desde Swagger podés usar el botón **Authorize** para pegar el token y probar
los endpoints protegidos.

## Correr los tests

```bash
pytest          # o: pytest -v
```

## Usuarios de ejemplo (tras `python seed.py`)

| Rol   | Email               | Password   |
|-------|---------------------|------------|
| admin | admin@tienda.com    | admin1234  |
| user  | user@tienda.com     | user1234   |

## Endpoints

| Método | Ruta                          | Descripción                         | Auth        |
|--------|-------------------------------|-------------------------------------|-------------|
| POST   | `/api/auth/register`          | Registrar usuario                   | Público     |
| POST   | `/api/auth/login`             | Login (devuelve JWT)                | Público     |
| GET    | `/api/auth/me`                | Perfil del usuario logueado         | Token       |
| GET    | `/api/categories`             | Listar categorías                   | Público     |
| GET    | `/api/categories/{id}`        | Detalle de categoría                | Público     |
| POST   | `/api/categories`             | Crear categoría                     | Admin       |
| PUT    | `/api/categories/{id}`        | Actualizar categoría                | Admin       |
| DELETE | `/api/categories/{id}`        | Eliminar categoría                  | Admin       |
| GET    | `/api/products`               | Listar productos (paginado/filtros) | Público     |
| GET    | `/api/products/search?q=`     | Buscar productos por nombre         | Público     |
| GET    | `/api/products/{id}`          | Detalle de producto                 | Público     |
| POST   | `/api/products`               | Crear producto                      | Admin       |
| PUT    | `/api/products/{id}`          | Actualizar producto                 | Admin       |
| DELETE | `/api/products/{id}`          | Eliminar producto                   | Admin       |
| GET    | `/api/users`                  | Listar usuarios                     | Admin       |

### Parámetros del listado de productos

- **Paginación**: `?page=1&per_page=20` (`per_page` máx. 100)
- **Filtros**: `?category_id=1&min_price=10&max_price=100`
- **Ordenamiento**: `?sort_by=price&order=asc` (`sort_by`: `name|price|stock|created_at`)

## Ejemplos con curl

```bash
# Registrar un usuario
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@example.com","full_name":"Ana García","password":"password123"}'

# Login (guardá el access_token de la respuesta)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tienda.com","password":"admin1234"}'

# Perfil propio (reemplazá $TOKEN)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Listar productos con filtros y orden
curl "http://localhost:8000/api/products?page=1&per_page=10&min_price=50&sort_by=price&order=asc"

# Buscar productos
curl "http://localhost:8000/api/products/search?q=notebook"

# Crear una categoría (requiere admin)
curl -X POST http://localhost:8000/api/categories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Electrónica","description":"Dispositivos electrónicos"}'

# Crear un producto (requiere admin)
curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook 14","price":799.99,"stock":15,"category_id":1}'
```

## Formato de errores

Todas las respuestas de error tienen la misma forma JSON:

```json
{ "error": { "code": 404, "message": "No existe el producto con id 99" } }
```

Los errores de validación (422) incluyen además `error.details` con el detalle
campo por campo de Pydantic.

## Notas de producción

- Para una base distinta a SQLite, cambiá `DATABASE_URL` en `.env`.
- El esquema se crea con `create_all` al arrancar; para producción conviene
  migraciones con **Alembic**.
- El rate limiting usa almacenamiento en memoria; con múltiples workers usá un
  backend compartido (Redis) configurando `slowapi`.
