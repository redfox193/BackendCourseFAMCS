import pytest


@pytest.fixture
def sample_list():
    return [1, 2, 3]


def test_list_length(sample_list):
    assert len(sample_list) == 3


def test_list_sum(sample_list):
    assert sum(sample_list) == 6


@pytest.mark.parametrize(
    ['new_items', 'length'],
    [
        ([1, 2, 3], 6),
        ([1, 2, 3, 4], 7),
    ]
)
def test_list_isolation(new_items, length, sample_list):
    # каждый тест получает свой экземпляр результата выполнения фикстуры
    sample_list.extend(new_items)
    assert len(sample_list) == length


@pytest.fixture
def first_item():
    return "a"

# фикстура зависит от другой фикстуры
@pytest.fixture
def order(first_item):
    return [first_item]


def test_order_append(order):
    order.append("b")
    assert order == ["a", "b"]


@pytest.fixture
def text_file(tmp_path):
    # tmp_path - библиотечная фикстура, путь к временному хранилищу для тестирования
    file_path = tmp_path / "example.txt"
    file_path.write_text("first line\nsecond line\n")
    f = file_path.open("r")
    yield f
    f.close()


def test_read_first_line(text_file):
    first_line = text_file.readline().strip()
    assert first_line == "first line"
