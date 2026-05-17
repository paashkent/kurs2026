from online_store.storage.json_storage import JsonStorage
from online_store.models.user import hash_password


def seed_database(storage: JsonStorage) -> None:
    data = storage.load()
    if data["products"] or data["users"]:
        return

    data["users"] = [
        {"id": 1, "username": "admin", "password": hash_password("admin123"), "role": "admin"},
        {"id": 2, "username": "user", "password": hash_password("user123"), "role": "customer"},
    ]
    data["products"] = [
        {"id": 1, "name": "Ноутбук Lenovo IdeaPad", "category": "Электроника", "price": 58990.0, "quantity": 8, "description": "Ноутбук для учебы и работы"},
        {"id": 2, "name": "Смартфон Samsung Galaxy", "category": "Электроника", "price": 34990.0, "quantity": 12, "description": "Смартфон среднего класса"},
        {"id": 3, "name": "Клавиатура Logitech", "category": "Периферия", "price": 2490.0, "quantity": 20, "description": "Проводная клавиатура"},
        {"id": 4, "name": "Мышь Xiaomi", "category": "Периферия", "price": 1290.0, "quantity": 25, "description": "Беспроводная мышь"},
        {"id": 5, "name": "Наушники JBL", "category": "Аудио", "price": 4990.0, "quantity": 15, "description": "Беспроводные наушники"},
    ]
    data["orders"] = []
    storage.save(data)
