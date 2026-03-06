## Fixtures

Фикстуры - это функции, логика которых выполняется до вызова теста. Они позволяют подготавливать данные и ресурсы для тестов.

### Базовое использование

Фикстура объявляется декоратором `@pytest.fixture`. Тест получает результат фикстуры, указав её имя в качестве аргумента:

```python
import pytest

@pytest.fixture
def sample_list():
    return [1, 2, 3]

def test_list_length(sample_list):
    assert len(sample_list) == 3

def test_list_sum(sample_list):
    assert sum(sample_list) == 6
```

Каждый тест получает свой экземпляр результата фикстуры - тесты изолированы друг от друга.

### Фикстуры могут зависеть от других фикстур

Фикстура может принимать другую фикстуру как аргумент:

```python
@pytest.fixture
def first_item():
    return "a"

@pytest.fixture
def order(first_item):
    return [first_item]

def test_order(order):
    order.append("b")
    assert order == ["a", "b"]
```

### yield-фикстуры

Если нужно добавить какую-то логику ПОСЛЕ выполнения теста, то 
используется слово `yield`. В этом случае `pytest` действует следующим образом:
- До начала теста:
  - Сначала он вызывает функцию и получает генератор
  - Выполняет `next()` для генератора, чтобы результат от `yield`
  - Передаёт результат в качестве аргумента в тест
- После выполенения теста
  - Для всех таких фикстур `pytest` возобновляет выполнение

```python
@pytest.fixture
def temp_file():
    f = open("/tmp/test.txt", "w")
    yield f
    f.close()
```

Код после `yield` выполнится после завершения теста (даже при падении).


### Scope (область видимости)

По умолчанию фикстура создаётся заново для каждого теста (`scope="function"`). Можно изменить поведение:

- `function` - для каждого теста (по умолчанию)
- `class` - один экземпляр на класс с тестами
- `module` - один экземпляр на файл
- `session` - один экземпляр на всю сессию запуска

```python
@pytest.fixture(scope="class")
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()

class TestDatabase:
    def test_one(self, db_connection):
        # используем одно соединение
        pass

    def test_two(self, db_connection):
        # то же соединение
        pass
```

### autouse

Фикстура с `autouse=True` выполняется автоматически для всех тестов в своей области, без явного указания в параметрах:

```python
@pytest.fixture(autouse=True)
def reset_state():
    # выполнится перед каждым тестом
    State.clear()
    yield
    # выполнится после каждого теста
    State.cleanup()
```

### conftest.py

Файл `conftest.py` - специальный файл pytest. Фикстуры, определённые в нём, автоматически доступны всем тестам в этой директории и поддиректориях. Импортировать их не нужно.

```
step_03/
├── conftest.py          # фикстуры для src/
└── src/
    ├── conftest.py      # фикстуры только для src/
    └── test_*.py
```

Фикстуры из более локальных `conftest` файлов переопределяют фикстуры с таким же именем
 пришедшие с более глобальных `conftest` файлов.