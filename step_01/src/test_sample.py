import pytest


def inc(x):
    return x + 1


def test_answer_must_fail():
    assert inc(3) == 5


def test_answer_must_success():
    assert inc(3) == 4


def test_sum():
    assert (0.1 + 0.2) == pytest.approx(0.3)