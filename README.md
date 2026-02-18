# FastAPI Observability Backend

Demo backend с FastAPI, структурированными логами и метриками Prometheus.

## Стек

- FastAPI + SQLAlchemy async + PostgreSQL
- Prometheus + Grafana + Loki + Alloy

## Запуск

### Docker Compose

```bash
docker compose up -d
```

| Сервис | URL |
|---|---|
| App | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |

### Локально

```bash
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt

# создать БД
createdb appdb

uvicorn app.main:app --reload
```

## Эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/process` | Обработка данных |
| GET | `/message/{id}` | Получить сообщение |
| GET | `/metrics` | Метрики Prometheus |

## Метрики

| Метрика | Тип | Описание |
|---|---|---|
| `app_requests_total` | Counter | Запросы по endpoint/status |
| `app_process_duration_seconds` | Histogram | Латентность /process |
| `app_db_query_duration_seconds` | Histogram | Время запросов к БД |

## Тесты

```bash
pip install pytest pytest-asyncio httpx aiosqlite anyio
pytest tests/ -v
```

Тесты используют SQLite через dependency override — PostgreSQL не нужен.
