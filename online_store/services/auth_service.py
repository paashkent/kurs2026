from online_store.models.user import Customer, Admin, User, user_from_dict, hash_password
from online_store.storage.json_storage import JsonStorage


class AuthService:
    """Регистрация, авторизация и администрирование пользователей."""

    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def register(self, username: str, password: str, role: str = "customer") -> User:
        if not username.strip():
            raise ValueError("Логин не может быть пустым")
        if len(password) < 4:
            raise ValueError("Пароль должен содержать не менее 4 символов")
        if role not in {"customer", "admin"}:
            raise ValueError("Недопустимая роль пользователя")

        data = self.storage.load()
        if any(user["username"] == username for user in data["users"]):
            raise ValueError("Пользователь с таким именем уже существует")

        user_id = self._next_id(data["users"])
        if role == "admin":
            user = Admin(id=user_id, username=username, password=hash_password(password))
        else:
            user = Customer(id=user_id, username=username, password=hash_password(password))

        data["users"].append(user.to_dict())
        self.storage.save(data)
        return user

    def login(self, username: str, password: str) -> User:
        data = self.storage.load()
        for user_data in data["users"]:
            user = user_from_dict(user_data)
            if user.username == username and user.check_password(password):
                return user
        raise ValueError("Неверный логин или пароль")

    def get_all_users(self) -> list[User]:
        """Возвращает список всех пользователей для админской панели."""
        return [user_from_dict(item) for item in self.storage.load()["users"]]

    def get_user_by_id(self, user_id: int) -> User:
        for user in self.get_all_users():
            if user.id == user_id:
                return user
        raise KeyError("Пользователь не найден")

    def update_user_role(self, user_id: int, role: str) -> User:
        """Изменяет роль пользователя: customer или admin."""
        if role not in {"customer", "admin"}:
            raise ValueError("Недопустимая роль пользователя")

        data = self.storage.load()
        for item in data["users"]:
            if item["id"] == user_id:
                item["role"] = role
                self.storage.save(data)
                return user_from_dict(item)
        raise KeyError("Пользователь не найден")

    def delete_user(self, user_id: int) -> None:
        """Удаляет пользователя, кроме стандартного администратора с ID 1."""
        if user_id == 1:
            raise ValueError("Нельзя удалить главного администратора")

        data = self.storage.load()
        initial_len = len(data["users"])
        data["users"] = [item for item in data["users"] if item["id"] != user_id]
        if len(data["users"]) == initial_len:
            raise KeyError("Пользователь не найден")
        self.storage.save(data)

    @staticmethod
    def _next_id(items: list[dict]) -> int:
        return max((item["id"] for item in items), default=0) + 1
