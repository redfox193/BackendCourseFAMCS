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


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(1, 2, 3), (2, 2, 5)],
    ids=["one_plus_two", "two_plus_two"],
)
def test_add_ids(a, b, expected):
    assert a + b == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(1, 2, 3, id="one_plus_two"),
        pytest.param(2, 2, 5, marks=pytest.mark.xfail, id="two_plus_two"),
    ],
)
def test_add_ids_fixed(a, b, expected):
    assert a + b == expected