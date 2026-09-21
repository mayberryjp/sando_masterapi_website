from waitress import serve

from sando_masterapi.api.app import create_app
from sando_masterapi.config import settings
from sando_masterapi.logging import configure_logging, get_logger


def main() -> None:
    configure_logging(settings.log_level)
    log = get_logger("api")
    app = create_app()
    log.info("starting api on %s:%s", settings.api_listen_address, settings.api_port)
    serve(app, host=settings.api_listen_address, port=settings.api_port)


if __name__ == "__main__":
    main()
