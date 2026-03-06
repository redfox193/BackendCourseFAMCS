from __future__ import annotations

import pathlib
import sys
import typing as tp

import pytest
from testsuite.databases.pgsql import discover

pytest_plugins = [
    # предоставляет фикстуры: mockserver, create_daemon_scope, ensure_daemon_started, create_service_client
    "testsuite.pytest_plugin",
    # предоставляет фикстуры: pgsql_local_create, pgsql_local, pgsql
    "testsuite.databases.pgsql.pytest_plugin",
]


DEMO_SERVICE_PORT = 18080
DEMO_SERVICE_URL = f"http://127.0.0.1:{DEMO_SERVICE_PORT}/"


# ------- Фикстуры конфигураторы --------


@pytest.fixture(scope="session")
def demo_root() -> pathlib.Path:
    """
    Возвращает корень приложения.
    """
    return pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
def pgsql_local(demo_root, pgsql_local_create):
    """
    - сканирует SQL-схемы в tests_blackbox/schemas/postgresql,
    - на основе user_db.sql регистрирует БД (user_db),
    - создает конфиг для запуска/инициализации PG в testsuite.
    """
    databases = discover.find_schemas(
        "demo_app",
        [demo_root.joinpath("tests_blackbox/schemas/postgresql")],
    )
    return pgsql_local_create(list(databases.values()))


@pytest.fixture(scope="session")
async def demo_service_scope(
    pytestconfig,
    create_daemon_scope,
    demo_root,
    pgsql_local,
    mockserver_info,
):
    """
    - сервис стартует командой python demo_app/server.py ...;
    - ему передается DSN БД и URL внешнего API;
    - ping_url проверяет readiness (/health), чтобы тесты не стартовали раньше.
    """
    async with create_daemon_scope(
        args=[
            sys.executable,
            str(demo_root.joinpath("server.py")),
            "--port",
            str(DEMO_SERVICE_PORT),
            "--postgresql",
            pgsql_local["user_db"].get_uri(),
            "--currency-api-base-url",
            mockserver_info.url("coingecko"), # http://localhost:<port>/coingecko
        ],
        ping_url=DEMO_SERVICE_URL + "health",
    ) as scope:
        yield scope


@pytest.fixture
async def demo_service(
    ensure_daemon_started,
    demo_service_scope,
    mockserver,
    pgsql,
):
    """
    Гарантирует, что процесс реально поднят и жив перед тестом.
    """
    await ensure_daemon_started(demo_service_scope)


@pytest.fixture
async def service_client(
    create_service_client,
    demo_service,
):
    """
    Клиент для сервиса
    """
    return create_service_client(DEMO_SERVICE_URL)


# ------- CoinGecko mockserver --------


class CurrencyApiMock:
    def __init__(self):
        self.price_response: tp.Optional[tp.Dict[str, tp.Any]] = {}
        self.price_status_code: int = 200
        self.last_query: tp.Optional[tp.Dict[str, tp.Any]] = None

    def set_price_response(
        self,
        response: tp.Dict[str, tp.Any],
        status_code: int = 200,
    ):
        self.price_response = response
        self.price_status_code = status_code


@pytest.fixture(name="mock_currency_api")
def _mock_currency_api(mockserver):
    mock = CurrencyApiMock()

    @mockserver.json_handler("/coingecko/simple/price")
    def _price_handler(*, query):
        mock.last_query = dict(query)
        return mockserver.make_response(
            json=mock.price_response,
            status=mock.price_status_code,
        )

    return mock
