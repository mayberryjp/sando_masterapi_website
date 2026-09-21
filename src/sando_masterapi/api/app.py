import json
from typing import Any

from bottle import Bottle, response

from sando_masterapi.api.routes.dashboard import register_dashboard_routes
from sando_masterapi.api.routes.errors import register_error_routes
from sando_masterapi.api.routes.health import register_health_routes

SERVICE_NAME = "sando-masterapi-api"


def create_app() -> Bottle:
    app = Bottle()
    app.title = SERVICE_NAME

    register_health_routes(app)
    register_dashboard_routes(app)
    register_error_routes(app)

    @app.hook("after_request")
    def enable_cors() -> None:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    @app.route("/<path:path>", method="OPTIONS")
    def cors_preflight(path: str) -> str:
        return ""

    @app.error(404)
    def not_found(_err: Any) -> str:
        response.content_type = "application/json"
        return json.dumps({"status": "error", "code": "not_found", "error": "not found"})

    return app


app = create_app()
