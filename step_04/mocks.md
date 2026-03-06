## Мокирование

Мокирование - подмена реальной зависимости тестовым объектом с предсказуемым поведением.

- **Изоляция юнит-теста** - убрать сеть, БД, файлы и т.п.
- **Детерминизм** - одинаковый результат при каждом запуске

**Термины:**
- **Mock** - объект, записывающий все вызовы; можно проверять
- **Stub** - объект с фиксированным ответом, без проверки вызовов
- **Fake** - рабочая упрощённая реализация (например, in-memory бд вместо PostgreSQL), отличается от 
предыдущих способов наличием внутреней логики

---

### monkeypatch

`monkeypatch` - встроенная фикстура pytest для подмены атрибутов, элементов словарей и переменных окружения. **Важно:** pytest автоматически откатывает все изменения после теста.

```python
def test_feature_flag(monkeypatch):
    monkeypatch.setenv("PAYMENTS_ENABLED", "0")
    # в тесте PAYMENTS_ENABLED == "0"
# после теста - исходное значение восстановлено
```

**Основные методы:**

| Метод | Назначение |
|-------|------------|
| `monkeypatch.setattr(obj, name, value)` | Подмена атрибута/функции/метода |
| `monkeypatch.delattr(obj, name)` | Удаление атрибута |
| `monkeypatch.setitem(mapping, key, value)` | Подмена элемента в dict |
| `monkeypatch.delitem(mapping, key)` | Удаление элемента |
| `monkeypatch.setenv(name, value)` | Установка переменной окружения |
| `monkeypatch.delenv(name)` | Удаление переменной окружения |

Примеры:
```python
# Подмена функции уровня модуля
monkeypatch.setattr("mymodule.fetch_data", lambda: {"temp": 25})

# Подмена класса
class FakeDataLoader:
    def get_json(self, path: str) -> dict:
        return {"path": path, "ok": True}

monkeypatch.setattr("mymodule.DataLoader", FakeDataLoader)

# Подмена константы
monkeypatch.setattr("app.config.API_URL", "http://fake.local")

# Подмена в словаре (конфиг, маппинг)
monkeypatch.setitem(os.environ, "DEBUG", "1")
# или проще:
monkeypatch.setenv("DEBUG", "1")
```

#### Асинхронные функции и monkeypatch

`monkeypatch` не различает sync/async — он просто меняет объект. Главное, чтобы вы подменили **awaitable** на awaitable:

```python
from unittest.mock import AsyncMock

from app.services.alert_service import check_and_alert_async


async def test_async_monkeypatch_with_function(monkeypatch):
    async def fake_fetch_weather(city: str) -> dict:
        return {"temp": 42}

    # Вариант 1: подмена на свою async-функцию
    monkeypatch.setattr(
        "app.services.alert_service.fetch_weather_async",
        fake_fetch_weather,
    )

    result = await check_and_alert_async("Rome", "user-1")
    assert result["temp"] == 42


async def test_async_monkeypatch_with_asyncmock(monkeypatch):
    async_fetch_mock = AsyncMock(return_value={"temp": 39})

    # Вариант 2: подмена на AsyncMock — можно проверять await-вызовы
    monkeypatch.setattr(
        "app.services.alert_service.fetch_weather_async",
        async_fetch_mock,
    )

    result = await check_and_alert_async("Berlin", "user-2")

    assert result["temp"] == 39
    async_fetch_mock.assert_awaited_once_with("Berlin")
```

---

### unittest.mock

#### patch

`patch` подменяет объект на время теста. В `patch` указывается путь к объекту по месту использования, который хотим замокать,
 вторым парамтером можно указать объект, которым хотим замокать, иначе объект будет замокирован дефолтным `Mock`
 объектом.

```python
# app/services/alert.py
from app.services.weather_client import get_weather  # импорт здесь

def check_alert(city: str) -> bool:
    data = get_weather(city)  # используется здесь
    return data["temp"] > 35

# tests/test_alert.py - патчим там, где используется!
from unittest.mock import patch

@patch("app.services.alert.get_weather")  # путь к get_weather в alert.py
def test_check_alert(mock_get_weather):
    mock_get_weather.return_value = {"temp": 40}
    assert check_alert("Moscow") is True
    mock_get_weather.assert_called_once_with("Moscow")
```

#### return_value и side_effect

`Mock` объект можно настраивать на ожидаемое поведение

```python
mock.return_value = 42            # при вызове объекта всегда возвращает 42
mock.side_effect = [1, 2, 3]      # первый вызов - 1, второй - 2, третий - 3
mock.side_effect = ValueError()   # при вызове бросает исключение
mock.side_effect = lambda x: x*2  # при вызове объекта на самом деле вызовет эту функцию
```

#### Проверка вызовов

`patch` лучше подходит, если хочется контроля и проверки, как с нашим замоканым объектом взаимодействовали

```python
mock.assert_called_once()
mock.assert_called_once_with("arg1", kwarg="value")
mock.assert_called_with("arg1")  # последний вызов с такими аргументами
mock.call_count                  # количество вызовов
mock.call_args                   # (args, kwargs) последнего вызова
mock.call_args_list              # список всех вызовов
```

#### AsyncMock

Обычный `Mock` не подходит для `async def` - он не awaitable. Надо использовать `AsyncMock`:

```python
from unittest.mock import AsyncMock, patch

@patch("app.services.weather_client.WeatherClient.fetch", new_callable=AsyncMock)
async def test_async_fetch(mock_fetch):
    mock_fetch.return_value = {"temp": 20}
    result = await some_async_function()
    assert result["temp"] == 20
    mock_fetch.assert_awaited_once()
```

#### Мокирование разных сущностей

| Сущность | Как патчить |
|----------|-------------|
| Функция модуля | `patch("module.func")` |
| Метод класса | `patch.object(MyClass, "method")` или `patch("module.MyClass.method")` |
| Класс целиком | `patch("module.MyClass", new=FakeClass)` |
| Синглтон/глобальный клиент | `patch("module.client")` - где client импортирован и используется |
