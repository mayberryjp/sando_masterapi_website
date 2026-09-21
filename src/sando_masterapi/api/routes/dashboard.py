import os

from bottle import Bottle, HTTPResponse, static_file

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


def register_dashboard_routes(app: Bottle) -> None:
    @app.get("/")
    def index() -> HTTPResponse:
        return static_file("index.html", root=STATIC_DIR)
