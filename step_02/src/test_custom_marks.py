import pytest

# маркер на весь модуль, применится ко всем тестам в этом файле
pytestmark = pytest.mark.demo


@pytest.mark.unit
def test_unit_example():
    assert True


@pytest.mark.integration
def test_integration_example():
    assert True


@pytest.mark.slow
def test_slow_example():
    assert True


@pytest.mark.webtest
class TestApiGroup:
    def test_a(self):
        # У теста будет маркер webtest от класса
        assert True

    @pytest.mark.slow
    def test_b_is_also_slow(self):
        # У теста будут сразу два маркера: webtest (от класса) и slow (локально)
        assert True


# pytest -m "smoke and not slow"
@pytest.mark.smoke
def test_smoke():
    assert True


# можно навешивать несколько маркеров
@pytest.mark.smoke
@pytest.mark.slow
def test_smoke_but_slow():
    assert True
