### Плагины

Плагины позволяют расширить возможности `pytest`.

На предыдущем шаге при написании интеграционных тестов мы столкнулись с тем,
 что для реализации black-box тестирования нам нужно самим позаботиться о 
 предварительном локальном запуске сервиса, его базы данных и подставных третьих сервисов 
(сервис для получения информции о курсах валют)

Рассмотрим плагин, который помогает облегчить подготовку, позволяя реализовывать полноценное 
black-box интеграционное тестирование.

### [testsuite](https://github.com/yandex/yandex-taxi-testsuite)

Testsuite изначально разрабатывался Яндексом для тестирования C++/Python микросервисов в black-box режиме.

#### Требования

Установить библиотеку

```shell
pip install yandex-taxi-testsuite
```

Подключим необходимые плагины в файл `tests_blackbox/conftest.py`:
```python
pytest_plugins = [
    # предоставляет фикстуры: mockserver, create_daemon_scope, ensure_daemon_started, create_service_client
    "testsuite.pytest_plugin",
    # предоставляет фикстуры: pgsql_local_create, pgsql_local, pgsql
    "testsuite.databases.pgsql.pytest_plugin",
]
```

Плагин `testsuite` предоставляет различные фикстуры, которые позволяют поднять сервис в отдельном процессе,
 поднять базу данных, и также поднять отдельный процесс, которые будет использоваться в качестве 
внешних сервисов.

#### Дополнительно

Для того, чтобы плагин мог поднимать бд PostgreSQL локально для тестов
 необходимо установить сервер Postgres:

```shell
brew install postgresql@16
```
На windows можно через [установщик](https://www.postgresql.org/download/windows/)

Дополнительно перед запускам тестов необходимо установить следующие перменные окружения:
```shell
export TESTSUITE_PGSQL_BINDIR="$(brew --prefix postgresql@16)/bin"
export PATH="$TESTSUITE_PGSQL_BINDIR:$PATH"

# windows
set TESTSUITE_PGSQL_BINDIR=C:\Program Files\PostgreSQL\16\bin
set PATH=%TESTSUITE_PGSQL_BINDIR%;%PATH%
```

В результате должен быть доступ из консоли к управлению Postgres сервером,
 проверить можно командой:
```python
which pg_ctl
pg_ctl --version
```