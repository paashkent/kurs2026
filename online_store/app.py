
from online_store.models.cart import Cart
from online_store.models.user import Admin
from online_store.services.auth_service import AuthService
from online_store.services.order_service import OrderService
from online_store.services.product_service import ProductService
from online_store.storage.json_storage import JsonStorage
from online_store.utils.seed_data import seed_database


class OnlineStoreApp:
    """Консольное приложение онлайн-магазина."""

    def __init__(self, database_path: str = "data/store.json"):
        self.storage = JsonStorage(database_path)
        seed_database(self.storage)
        self.auth_service = AuthService(self.storage)
        self.product_service = ProductService(self.storage)
        self.order_service = OrderService(self.storage)
        self.cart = Cart()
        self.current_user = None

    def run(self) -> None:
        print("Система управления онлайн-магазином")
        while True:
            try:
                if self.current_user is None:
                    self._auth_menu()
                elif isinstance(self.current_user, Admin):
                    self._admin_menu()
                else:
                    self._customer_menu()
            except Exception as error:
                print(f"Ошибка: {error}")

    def _auth_menu(self) -> None:
        print("\n1. Войти")
        print("2. Зарегистрироваться")
        print("0. Выход")
        choice = input("Выберите действие: ")
        if choice == "1":
            username = input("Логин: ")
            password = input("Пароль: ")
            self.current_user = self.auth_service.login(username, password)
            print(f"Вход выполнен: {self.current_user.username} ({self.current_user.role})")
        elif choice == "2":
            username = input("Логин: ")
            password = input("Пароль: ")
            self.current_user = self.auth_service.register(username, password)
            print("Регистрация выполнена")
        elif choice == "0":
            raise SystemExit
        else:
            print("Некорректный пункт меню")

    def _customer_menu(self) -> None:
        print("\n=== Добро пожаловать! ===")
        print("1. Показать каталог")
        print("2. Поиск товаров по названию или категории")
        print("3. Поиск товара по ID")
        print("4. Добавить товар в корзину")
        print("5. Показать корзину")
        print("6. Удалить товар из корзины")
        print("7. Оформить заказ")
        print("8. История заказов")
        print("9. Поиск заказа по ID")
        print("10. Отменить заказ")
        print("11. Выйти из аккаунта")
        choice = input("Выберите действие: ")
        if choice == "1":
            self._show_products(self.product_service.get_all())
        elif choice == "2":
            query = input("Введите название или категорию: ")
            self._show_products(self.product_service.search(query))
        elif choice == "3":
            self._search_product_by_id()
        elif choice == "4":
            product_id = int(input("ID товара: "))
            quantity = int(input("Количество: "))
            product = self.product_service.get_by_id(product_id)
            self.cart.add_product(product, quantity)
            print("Товар добавлен в корзину")
        elif choice == "5":
            self._show_cart()
        elif choice == "6":
            self._remove_from_cart()
        elif choice == "7":
            products = self.product_service.get_all()
            order = self.order_service.create_order(self.current_user.id, self.cart, products)
            print(f"Заказ №{order.id} оформлен. Сумма: {order.total} руб.")
        elif choice == "8":
            orders = self.order_service.get_orders_by_user(self.current_user.id)
            self._show_orders(orders)
        elif choice == "9":
            self._search_customer_order_by_id()
        elif choice == "10":
            self._cancel_customer_order()
        elif choice == "11":
            self.current_user = None
            self.cart.clear()
        else:
            print("Некорректный пункт меню")

    def _search_product_by_id(self) -> None:
        product_id_raw = input("Введите ID товара: ").strip()

        if not product_id_raw.isdigit():
            print("Ошибка: ID товара должен быть числом")
            return

        product_id = int(product_id_raw)
        product = self.product_service.get_by_id(product_id)
        self._show_products([product])

    def _remove_from_cart(self) -> None:
        if self.cart.is_empty():
            print("Корзина пуста")
            return

        self._show_cart()
        product_id = int(input("ID товара для удаления: "))
        quantity_raw = input("Количество для удаления, Enter — удалить полностью: ").strip()

        if quantity_raw:
            quantity = int(quantity_raw)
            self.cart.remove_product(product_id, quantity)
        else:
            self.cart.remove_product(product_id)

        print("Товар удален из корзины")

    def _cancel_customer_order(self) -> None:
        orders = self.order_service.get_orders_by_user(self.current_user.id)
        if not orders:
            print("У вас нет заказов")
            return

        self._show_orders(orders)
        order_id = int(input("ID заказа для отмены: "))
        order = self.order_service.cancel_order_by_user(order_id, self.current_user.id)
        print(f"Заказ №{order.id} отменен")

    def _admin_menu(self) -> None:
        print("\n=== Админ-панель ===")
        print("1. Показать каталог")
        print("2. Поиск товара по ID")
        print("3. Добавить товар")
        print("4. Изменить товар")
        print("5. Удалить товар")
        print("6. Показать все заказы")
        print("7. Поиск заказа по ID")
        print("8. Изменить статус заказа")
        print("9. Показать пользователей")
        print("10. Изменить роль пользователя")
        print("11. Удалить пользователя")
        print("12. Отчет по магазину")
        print("0. Выйти из аккаунта")
        choice = input("Выберите действие: ")
        if choice == "1":
            self._show_products(self.product_service.get_all())
        elif choice == "2":
            self._search_product_by_id()
        elif choice == "3":
            self._admin_add_product()
        elif choice == "4":
            self._admin_update_product()
        elif choice == "5":
            product_id = int(input("ID товара: "))
            product = self.product_service.get_by_id(product_id)
            confirm = input(f"Удалить товар '{product.name}'? (y/n): ").lower().strip()
            if confirm == "y":
                self.product_service.delete_product(product_id)
                print("Товар удален")
            else:
                print("Удаление отменено")
        elif choice == "6":
            self._show_orders(self.order_service.get_all_orders())
        elif choice == "7":
            self._search_order_by_id()
        elif choice == "8":
            self._admin_update_order_status()
        elif choice == "9":
            self._show_users(self.auth_service.get_all_users())
        elif choice == "10":
            self._admin_update_user_role()
        elif choice == "11":
            user_id = int(input("ID пользователя: "))
            user = self.auth_service.get_user_by_id(user_id)
            confirm = input(f"Удалить пользователя '{user.username}'? (y/n): ").lower().strip()
            if confirm == "y":
                self.auth_service.delete_user(user_id)
                print("Пользователь удален")
            else:
                print("Удаление отменено")
        elif choice == "12":
            self._show_admin_report()
        elif choice == "0":
            self.current_user = None
        else:
            print("Некорректный пункт меню")

    @staticmethod
    def _format_order_status(status: str) -> str:
        statuses = {
            "created": "создан",
            "paid": "оплачен",
            "shipped": "отправлен",
            "completed": "завершен",
            "cancelled": "отменен",
        }
        return statuses.get(status, status)

    def _search_order_by_id(self) -> None:
        order_id_raw = input("Введите ID заказа: ").strip()

        if not order_id_raw.isdigit():
            print("Ошибка: ID заказа должен быть числом")
            return

        order_id = int(order_id_raw)
        order = self.order_service.get_order_by_id(order_id)
        self._show_orders([order])

    def _admin_add_product(self) -> None:
        name = input("Название: ")
        category = input("Категория: ")
        price = float(input("Цена: "))
        quantity = int(input("Количество: "))
        if quantity < 0:
            raise ValueError("Количество не может быть меньше 0")
        description = input("Описание: ")
        product = self.product_service.add_product(name, category, price, quantity, description)
        print(f"Товар добавлен с ID {product.id}")

    def _admin_update_product(self) -> None:
        product_id = int(input("ID товара: "))
        name = input("Новое название, Enter — не менять: ") or None
        category = input("Новая категория, Enter — не менять: ") or None
        price_raw = input("Новая цена, Enter — не менять: ")
        quantity_raw = input("Новое количество, Enter — не менять: ")
        if quantity_raw and int(quantity_raw) < 0:
            raise ValueError("Количество не может быть меньше 0")
        description = input("Новое описание, Enter — не менять: ") or None
        self.product_service.update_product(
            product_id,
            name=name,
            category=category,
            price=float(price_raw) if price_raw else None,
            quantity=int(quantity_raw) if quantity_raw else None,
            description=description,
        )
        print("Товар обновлен")

    def _admin_update_order_status(self) -> None:
        orders = self.order_service.get_all_orders()
        if not orders:
            print("Заказы отсутствуют")
            return

        print("\nСписок заказов:")
        self._show_orders(orders)

        order_id_raw = input("Введите ID заказа: ").strip()
        if not order_id_raw.isdigit():
            print("Ошибка: ID заказа должен быть числом")
            return

        order_id = int(order_id_raw)

        status_map = {
            "1": "created",
            "2": "paid",
            "3": "shipped",
            "4": "completed",
            "5": "cancelled",
        }

        print("\nВыберите новый статус:")
        print("1. created — создан")
        print("2. paid — оплачен")
        print("3. shipped — отправлен")
        print("4. completed — завершен")
        print("5. cancelled — отменен")

        status_choice = input("Номер статуса: ").strip()
        status = status_map.get(status_choice)

        if status is None:
            print("Ошибка: выбран некорректный статус")
            return

        order = self.order_service.update_order_status(order_id, status)
        print(f"Статус заказа №{order.id} изменен на {self._format_order_status(order.status)}")

    def _admin_update_user_role(self) -> None:
        user_id = int(input("ID пользователя: "))
        role = input("Новая роль (customer/admin): ")
        user = self.auth_service.update_user_role(user_id, role)
        print(f"Роль пользователя {user.username} изменена на {user.role}")

    def _show_admin_report(self) -> None:
        products = self.product_service.get_all()
        users = self.auth_service.get_all_users()
        orders = self.order_service.get_all_orders()
        total_revenue = sum(order.total for order in orders if order.status != "cancelled")
        low_stock = [product for product in products if 0 <= product.quantity <= 3]

        print("\nОтчет по магазину:")
        print(f"Товаров в каталоге: {len(products)}")
        print(f"Пользователей: {len(users)}")
        print(f"Заказов: {len(orders)}")
        print(f"Выручка по неотмененным заказам: {total_revenue} руб.")
        if low_stock:
            print("Товары с низким остатком:")
            for product in low_stock:
                print(
                    f"ID: {product.id} | "
                    f"{product.name} | "
                    f"{product.price} ₽ | "
                    f"Остаток: {product.quantity}"
                )
        else:
            print("Товаров с низким остатком нет")

    @staticmethod
    def _show_products(products) -> None:
        if not products:
            print("Товары не найдены")
            return
        print("\nКаталог товаров:")
        for product in products:
            print(
                f"ID: {product.id} | "
                f"{product.name} | "
                f"{product.price} ₽ | "
                f"Остаток: {product.quantity}"
            )

    def _show_cart(self) -> None:
        if self.cart.is_empty():
            print("Корзина пуста")
            return
        print("\nКорзина:")
        for item in self.cart.items.values():
            print(
                f"ID: {item.product_id} | "
                f"{item.name}: {item.quantity} шт. x {item.price} = {item.total} руб."
            )
        print(f"Итого: {self.cart.total_price()} руб.")

    def _show_orders(self, orders) -> None:
        if not orders:
            print("Заказы отсутствуют")
            return
        for order in orders:
            status_text = self._format_order_status(order.status)
            print(
                f"Заказ №{order.id} | "
                f"пользователь: {order.user_id} | "
                f"сумма: {order.total} | "
                f"статус: {status_text} | "
                f"дата: {order.created_at}"
            )

    @staticmethod
    def _show_users(users) -> None:
        if not users:
            print("Пользователи отсутствуют")
            return
        print("\nПользователи:")
        for user in users:
            print(f"{user.id}. {user.username} | роль: {user.role}")


if __name__ == "__main__":
    OnlineStoreApp().run()
