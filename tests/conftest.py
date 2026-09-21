import pytest
from webtest import TestApp

from sando_masterapi.api.app import create_app


@pytest.fixture
def app() -> TestApp:
    return TestApp(create_app())
