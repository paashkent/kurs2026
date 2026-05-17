from dataclasses import dataclass, field
from typing import Dict

from online_store.models.product import Product


@dataclass
class CartItem:
    product_id: int
    name: str
    price: float
    quantity: int

    @property
    def total(self) -> float:
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
        }


@dataclass
class Cart:
    """Корзина покупателя."""
    items: Dict[int, CartItem] = field(default_factory=dict)

    def add_product(self, product: Product, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        current_quantity = self.items[product.id].quantity if product.id in self.items else 0
        if current_quantity + quantity > product.quantity:
            raise ValueError("На складе недостаточно товара")

        if product.id in self.items:
            self.items[product.id].quantity += quantity
        else:
            self.items[product.id] = CartItem(product.id, product.name, product.price, quantity)

    def remove_product(self, product_id: int, quantity: int | None = None) -> None:
        """Удаляет товар из корзины полностью или уменьшает его количество."""
        if product_id not in self.items:
            raise KeyError("Товар не найден в корзине")

        if quantity is None:
            del self.items[product_id]
            return

        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        if quantity >= self.items[product_id].quantity:
            del self.items[product_id]
        else:
            self.items[product_id].quantity -= quantity

    def clear(self) -> None:
        self.items.clear()

    def is_empty(self) -> bool:
        return not self.items

    def total_price(self) -> float:
        return round(sum(item.total for item in self.items.values()), 2)

    def to_list(self) -> list[dict]:
        return [item.to_dict() for item in self.items.values()]
