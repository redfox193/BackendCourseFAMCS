import pytest

def parse_age(s: str) -> int:
    if not s.isdigit():
        raise ValueError("age must be a number")
    return int(s)

def test_parse_age_rejects_non_digits():
    with pytest.raises(ValueError, match="age must be a number"):
        parse_age("abc")