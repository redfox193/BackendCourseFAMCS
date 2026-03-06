import sys
import pytest


pytestmark = pytest.mark.skipif(sys.version_info < (3, 11), reason="Нужен Python 3.11+")


@pytest.mark.skip(reason="not implemented")
def test_new_python_posix_only():
    assert True


@pytest.mark.skipif(sys.platform == "win32", reason="Не запускаем на Windows")
def test_new_python_posix_only_2():
    assert True


@pytest.mark.xfail(strict=True, raises=ZeroDivisionError, reason="Известно: пока делим на ноль в edge-case")
def test_known_exception_type():
    assert 1 / 0  == 0
