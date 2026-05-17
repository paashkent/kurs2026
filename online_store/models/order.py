from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Order:
    """Заказ покупателя."""
    id: int
    user_id: int
    items: list[dict]
    total: float
    status: str = "created"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def change_status(self, status: str) -> None:
        allowed = {"created", "paid", "shipped", "completed", "cancelled"}
        if status not in allowed:
            raise ValueError("Недопустимый статус заказа")
        self.status = status

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Order":
        return Order(**data)
