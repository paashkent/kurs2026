from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib


def hash_password(password: str) -> str:
    """Возвращает SHA-256 хеш пароля."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass
class User(ABC):
    """Базовый пользователь системы."""
    id: int
    username: str
    password: str
    role: str

    @abstractmethod
    def get_permissions(self) -> list[str]:
        pass

    def check_password(self, password: str) -> bool:
        return self.password == hash_password(password)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Customer(User):
    role: str = "customer"

    def get_permissions(self) -> list[str]:
        return ["view_products", "use_cart", "create_order", "view_orders"]


@dataclass
class Admin(User):
    role: str = "admin"

    def get_permissions(self) -> list[str]:
        return ["view_products", "manage_products", "view_orders"]


def user_from_dict(data: dict) -> User:
    if data.get("role") == "admin":
        return Admin(**data)
    return Customer(**data)
