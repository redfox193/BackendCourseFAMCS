from app.models import User, UserCreate, UserUpdate


class FakeUserRepository:

    def __init__(self):
        self._storage: dict[int, User] = {}
        self._next_id = 1

    def get_all(self) -> list[User]:
        return list(self._storage.values())

    def get_by_id(self, user_id: int) -> User | None:
        return self._storage.get(user_id)

    def create(self, data: UserCreate) -> User:
        user = User(id=self._next_id, username=data.username, name=data.name)
        self._storage[self._next_id] = user
        self._next_id += 1
        return user

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        if user_id not in self._storage:
            return None
        user = self._storage[user_id]
        if data.username is not None:
            user = user.model_copy(update={"username": data.username})
        if data.name is not None:
            user = user.model_copy(update={"name": data.name})
        self._storage[user_id] = user
        return user

    def delete(self, user_id: int) -> bool:
        if user_id in self._storage:
            del self._storage[user_id]
            return True
        return False


class FakeCurrencyRatesClient:

    def __init__(self, rates: dict[str, float] | None = None):
        self._rates = rates or {"BTC": 50000.0, "ETH": 3000.0, "SOL": 100.0}

    def get_rates_usd(self, symbols: list[str]) -> dict[str, float]:
        return {s: self._rates.get(s, 0.0) for s in symbols}
