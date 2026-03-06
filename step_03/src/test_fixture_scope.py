import pytest

call_count = 0


@pytest.fixture(scope="function")
def function_scope_fixture():
    """По умолчанию — новый экземпляр для каждого теста."""
    global call_count
    call_count += 1
    return call_count


def test_function_scope_a(function_scope_fixture):
    assert function_scope_fixture == 1


def test_function_scope_b(function_scope_fixture):
    # другой тест — другой вызов фикстуры
    assert function_scope_fixture == 2


@pytest.fixture(scope="class")
def class_scope_value():
    """Один экземпляр на класс."""
    return {"created": True}


class TestClassScope:
    def test_first(self, class_scope_value):
        class_scope_value["key"] = True
        assert class_scope_value["created"]

    def test_second(self, class_scope_value):
        # тот же объект — first уже есть
        assert class_scope_value.get("key") is True


@pytest.fixture(scope="module")
def module_scope_counter():
    """Один экземпляр на модуль."""
    return {"count": 0}


def test_module_scope_a(module_scope_counter):
    module_scope_counter["count"] += 1
    assert module_scope_counter["count"] == 1


def test_module_scope_b(module_scope_counter):
    # тот же объект из предыдущего теста
    module_scope_counter["count"] += 1
    assert module_scope_counter["count"] == 2


# autouse — выполняется автоматически для всех тестов в модуле
_autouse_log = []


@pytest.fixture(autouse=True)
def auto_reset():
    """Выполняется перед и после каждого теста в этом файле."""
    _autouse_log.append("before")
    yield
    _autouse_log.append("after")


def test_autouse_executed():
    assert "before" in _autouse_log


def test_autouse_runs_per_test():
    assert _autouse_log.count("before") == 8 # так как всего 8 тестов в файле
    assert _autouse_log.count("after") == 7 # так как after для этого теста ещё не был добавлен
