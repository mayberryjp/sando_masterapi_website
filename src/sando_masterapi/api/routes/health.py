from bottle import Bottle, response

from sando_masterapi.db import check_database


def register_health_routes(app: Bottle) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "sando-masterapi-api"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        ok, detail = check_database()
        if not ok:
            response.status = 503
            return {"status": "error", "code": "not_ready", "error": detail}
        return {"status": "ok"}
