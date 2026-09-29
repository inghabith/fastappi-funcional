# FastAPI + Docker

API de inventario de productos con FastAPI, SQLModel, Alembic y PostgreSQL.

## Configuración

```bash
cp .env.example .env   # y completa DATABASE_URL con tus credenciales
```

## Ejecutar con Docker

```bash
docker compose up --build
```

El contenedor aplica las migraciones (`alembic upgrade head`) y luego inicia el servidor en http://localhost:8000 (docs en `/docs`).

## Ejecutar en local

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev main.py
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/product` | Crea un producto (409 si el nombre ya existe, 422 si los datos son inválidos) |
| GET | `/product` | Lista los productos |
| DELETE | `/product/{product_id}` | Elimina un producto (404 si no existe) |

## Migraciones

```bash
uv run alembic revision --autogenerate -m "descripcion"
uv run alembic upgrade head
```
