## Marks

Декоратор `@pytest.mark` используется для того, чтобы обогощать тест какими-либо 
метаданными. Позволяет управлять отбором тестов, их поведением и настройками запуска.

Пример теста с маркером:
```python
@pytest.mark.small
def test_sum():
    assert True
```

Чтобы запустить тесты с определенным маркером необходимо написать:

Также рекомендуется фиксировать такие кастомные маркеры в конфиге:
```ini
[pytest]
markers =
    small: for small tests
```

### поведенческие маркеры

- `@pytest.mark.skip(reason="...")` - пропустить тест.
- `@pytest.mark.skipif(condition, reason="...")` - пропустить при условии.
- `@pytest.mark.xfail(reason="...", strict=..., raises=...)` - ожидаемое падение (например, известный баг).

Пример:
```python
@pytest.mark.skipif(sys.version_info < (3, 11), reason="Нужен Python 3.11+")
@pytest.mark.skipif(sys.platform == "win32", reason="Не запускаем на Windows")
def test_new_python_posix_only():
    assert True

# strict - означает, что тест обязан падать, иначе будет засчитан как failed
# raise - отлавливает только подения из-за конкретного исключения
@pytest.mark.xfail(strict=True, raises=ZeroDivisionError, reason="Известно: пока делим на ноль в edge-case")
def test_known_exception_type():
    assert 1 / 0  == 0
```

### pytest.mark.parametrize

Один из полезных маркеров, позволяет запустить один тест несколько раз с различными аргуменатми

Синткасис
```python
import pytest

def add(a, b):
    return a + b

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 5, 4),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```
- сначала в кортеже идут аргументы
- далее идет список конкретных значений аргументов

Чтобы удобео отслеживать упавшие кейсы можно дополнительно указывать `ids`
```python
import pytest

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(1, 2, 3), (2, 2, 4)],
    ids=["one_plus_two", "two_plus_two"],
)
def test_add_ids(a, b, expected):
    assert a + b == expected
```

Также кейсам из `paramtrize` можно навешивать маркеры, используя `pytest.param`:
```python
@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3), 
        pytest.param(2, 2, 5, marks)
    ],
    ids=["one_plus_two", "two_plus_two"],
)
def test_add_ids(a, b, expected):
    assert a + b == expected
```

### pytest.mark.asyncio

Для тестирования асинхронных функций необходимо либо
 помечать их маркером `@pytest.mark.asyncio`, который говорит `pytest`, что это асинхронный тест и его 
и его нужно выполнять внутри event loop, либо включить это поведение по умолчанию в `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
```

Пример:

```python
import asyncio
import pytest


async def get_answer_after_delay(delay: float) -> int:
    await asyncio.sleep(delay)
    return 42


@pytest.mark.asyncio
async def test_get_answer_after_delay():
    result = await get_answer_after_delay(0)
    assert result == 42
```