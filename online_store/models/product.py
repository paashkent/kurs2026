from dataclasses import dataclass, asdict


@dataclass
class Product:
    """Товар онлайн-магазина."""
    id: int
    name: str
    category: str
    price: float
    quantity: int
    description: str = ""

    def __post_init__(self) -> None:
        if self.quantity is None:
            self.quantity = 0
        self.quantity = int(self.quantity)
        if self.quantity < 0:
            self.quantity = 0

    def decrease_quantity(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Количество должно быть положительным")
        if amount > self.quantity:
            raise ValueError("Недостаточно товара на складе")
        self.quantity -= amount

    def increase_quantity(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Количество должно быть положительным")
        self.quantity += amount

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Product":
        return Product(**data)
