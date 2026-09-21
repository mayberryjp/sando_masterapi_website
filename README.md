# sando_masterapi

Error reports dashboard API (Bottle + Waitress, SQLAlchemy over SQLite).

## Local runbook

```bash
# install (editable with dev tools)
pip install .[dev]

# run the API (serves the dashboard on http://localhost:5000)
python -m sando_masterapi

# test / lint / typecheck
pytest -q
ruff check .
mypy src

# run under Docker
docker compose up
```

## Configuration

All configuration is supplied through environment variables (see `docker-compose.yml`):

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:////database/errors.db` | SQLAlchemy URL for the error-reports database (read-only). |
| `API_LISTEN_ADDRESS` | `0.0.0.0` | Address the API binds to. |
| `API_PORT` | `5000` | Port the API listens on. |

## Endpoints

- `GET /health` — process liveness.
- `GET /ready` — database readiness.
- `GET /` — dashboard UI.
- `GET /api/*` — dashboard data endpoints.
