from online_store.models.product import Product
from online_store.storage.json_storage import JsonStorage


class ProductService:
    """Работа с каталогом товаров."""

    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def get_all(self) -> list[Product]:
        return [Product.from_dict(item) for item in self.storage.load()["products"]]

    def get_by_id(self, product_id: int) -> Product:
        for product in self.get_all():
            if product.id == product_id:
                return product
        raise KeyError("Товар не найден")

    def search(self, query: str) -> list[Product]:
        query = query.lower().strip()
        return [
            product for product in self.get_all()
            if query in product.name.lower() or query in product.category.lower()
        ]

    def add_product(self, name: str, category: str, price: float, quantity: int, description: str = "") -> Product:
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")

        data = self.storage.load()
        product = Product(
            id=self._next_id(data["products"]),
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            description=description,
        )
        data["products"].append(product.to_dict())
        self.storage.save(data)
        return product

    def update_product(self, product_id: int, **kwargs) -> Product:
        if "price" in kwargs and kwargs["price"] is not None and kwargs["price"] <= 0:
            raise ValueError("Цена должна быть положительной")
        if "quantity" in kwargs and kwargs["quantity"] is not None and kwargs["quantity"] < 0:
            raise ValueError("Количество не может быть отрицательным")

        data = self.storage.load()
        for item in data["products"]:
            if item["id"] == product_id:
                item.update({key: value for key, value in kwargs.items() if value is not None})
                product = Product.from_dict(item)
                item.update(product.to_dict())
                self.storage.save(data)
                return product
        raise KeyError("Товар не найден")

    def delete_product(self, product_id: int) -> None:
        data = self.storage.load()
        initial_len = len(data["products"])
        data["products"] = [item for item in data["products"] if item["id"] != product_id]
        if len(data["products"]) == initial_len:
            raise KeyError("Товар не найден")
        self.storage.save(data)

    def save_products(self, products: list[Product]) -> None:
        data = self.storage.load()
        data["products"] = [product.to_dict() for product in products]
        self.storage.save(data)

    @staticmethod
    def _next_id(items: list[dict]) -> int:
        return max((item["id"] for item in items), default=0) + 1
