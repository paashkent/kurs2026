from online_store.models.cart import Cart
from online_store.models.order import Order
from online_store.models.product import Product
from online_store.storage.json_storage import JsonStorage


class OrderService:
    """Оформление заказов, история покупок и управление статусами."""

    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def create_order(self, user_id: int, cart: Cart, products: list[Product]) -> Order:
        if cart.is_empty():
            raise ValueError("Корзина пуста")

        product_map = {product.id: product for product in products}
        for item in cart.items.values():
            if item.product_id not in product_map:
                raise KeyError("Один из товаров не найден")
            product_map[item.product_id].decrease_quantity(item.quantity)

        data = self.storage.load()
        order = Order(
            id=self._next_id(data["orders"]),
            user_id=user_id,
            items=cart.to_list(),
            total=cart.total_price(),
        )
        data["products"] = [product.to_dict() for product in products]
        data["orders"].append(order.to_dict())
        self.storage.save(data)
        cart.clear()
        return order

    def get_orders_by_user(self, user_id: int) -> list[Order]:
        data = self.storage.load()
        return [Order.from_dict(item) for item in data["orders"] if item["user_id"] == user_id]

    def get_all_orders(self) -> list[Order]:
        return [Order.from_dict(item) for item in self.storage.load()["orders"]]

    def get_order_by_id(self, order_id: int) -> Order:
        for order in self.get_all_orders():
            if order.id == order_id:
                return order
        raise KeyError("Заказ не найден")

    def update_order_status(self, order_id: int, status: str) -> Order:
        """Изменяет статус заказа из админской панели."""
        data = self.storage.load()
        for item in data["orders"]:
            if item["id"] == order_id:
                order = Order.from_dict(item)
                order.change_status(status)
                item.update(order.to_dict())
                self.storage.save(data)
                return order
        raise KeyError("Заказ не найден")

    def cancel_order_by_user(self, order_id: int, user_id: int) -> Order:
        """Отменяет заказ покупателем и возвращает товары на склад."""
        data = self.storage.load()

        for item in data["orders"]:
            if item["id"] == order_id and item["user_id"] == user_id:
                order = Order.from_dict(item)

                if order.status == "cancelled":
                    raise ValueError("Заказ уже отменен")
                if order.status in {"shipped", "completed"}:
                    raise ValueError("Нельзя отменить отправленный или завершенный заказ")

                order.change_status("cancelled")
                item.update(order.to_dict())

                product_map = {product["id"]: product for product in data["products"]}
                for order_item in order.items:
                    product = product_map.get(order_item["product_id"])
                    if product is not None:
                        product["quantity"] += order_item["quantity"]

                self.storage.save(data)
                return order

        raise KeyError("Заказ не найден")

    @staticmethod
    def _next_id(items: list[dict]) -> int:
        return max((item["id"] for item in items), default=0) + 1
