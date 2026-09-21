from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from sando_masterapi.config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
    return _engine


def check_database() -> tuple[bool, str]:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, f"database check failed: {type(exc).__name__}"
