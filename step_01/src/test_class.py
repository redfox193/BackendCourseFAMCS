class TestClass:
    def test_one(self):
        assert True

    def test_two(self):
        assert False


class TestClassShared:
    value = 0

    def test_one(self):
        self.value = 1
        assert self.value == 1

    def test_two(self):
        assert self.value == 1

    @classmethod
    def test_three(cls):
        assert cls.value == 0
        cls.value = 1
        assert cls.value == 1

    @classmethod
    def test_four(cls):
        assert cls.value == 1