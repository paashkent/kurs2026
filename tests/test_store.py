import tempfile
import unittest

from online_store.models.cart import Cart
from online_store.services.auth_service import AuthService
from online_store.services.order_service import OrderService
from online_store.services.product_service import ProductService
from online_store.storage.json_storage import JsonStorage


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.storage = JsonStorage(self.temp_file.name)
        self.auth_service = AuthService(self.storage)
        self.product_service = ProductService(self.storage)
        self.order_service = OrderService(self.storage)

    def test_register_and_login(self):
        user = self.auth_service.register("ivan", "12345")
        logged_user = self.auth_service.login("ivan", "12345")
        self.assertEqual(user.username, logged_user.username)
        self.assertEqual(logged_user.role, "customer")


    def test_password_is_hashed(self):
        user = self.auth_service.register("secure_user", "12345")
        self.assertNotEqual(user.password, "12345")
        self.assertTrue(self.auth_service.login("secure_user", "12345"))

    def test_add_and_search_product(self):
        self.product_service.add_product("Тестовый ноутбук", "Электроника", 1000, 5)
        result = self.product_service.search("ноутбук")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].category, "Электроника")

    def test_get_product_by_id(self):
        product = self.product_service.add_product("SSD", "Комплектующие", 4500, 7)
        found_product = self.product_service.get_by_id(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, "SSD")


    def test_get_order_by_id(self):
        user = self.auth_service.register("order_finder", "12345")
        product = self.product_service.add_product("USB Hub", "Периферия", 1500, 6)
        cart = Cart()
        cart.add_product(product, 1)

        order = self.order_service.create_order(user.id, cart, self.product_service.get_all())
        found_order = self.order_service.get_order_by_id(order.id)

        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.user_id, user.id)

    def test_create_order(self):
        user = self.auth_service.register("petr", "12345")
        product = self.product_service.add_product("Мышь", "Периферия", 500, 10)
        cart = Cart()
        cart.add_product(product, 2)
        products = self.product_service.get_all()
        order = self.order_service.create_order(user.id, cart, products)
        self.assertEqual(order.total, 1000)
        self.assertTrue(cart.is_empty())
        updated_product = self.product_service.get_by_id(product.id)
        self.assertEqual(updated_product.quantity, 8)


class AdminPanelTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.storage = JsonStorage(self.temp_file.name)
        self.auth_service = AuthService(self.storage)
        self.product_service = ProductService(self.storage)
        self.order_service = OrderService(self.storage)

    def test_admin_can_change_user_role(self):
        user = self.auth_service.register("manager", "12345")
        updated_user = self.auth_service.update_user_role(user.id, "admin")
        self.assertEqual(updated_user.role, "admin")
        self.assertEqual(updated_user.get_permissions(), ["view_products", "manage_products", "view_orders"])

    def test_admin_can_change_order_status(self):
        user = self.auth_service.register("buyer", "12345")
        product = self.product_service.add_product("Монитор", "Электроника", 12000, 4)
        cart = Cart()
        cart.add_product(product, 1)
        order = self.order_service.create_order(user.id, cart, self.product_service.get_all())
        updated_order = self.order_service.update_order_status(order.id, "shipped")
        self.assertEqual(updated_order.status, "shipped")

    def test_main_admin_cannot_be_deleted(self):
        self.auth_service.register("main_admin", "12345", role="admin")
        with self.assertRaises(ValueError):
            self.auth_service.delete_user(1)

    def test_remove_product_from_cart(self):
        product = self.product_service.add_product("Клавиатура", "Периферия", 2000, 5)
        cart = Cart()
        cart.add_product(product, 3)

        cart.remove_product(product.id, 1)
        self.assertEqual(cart.items[product.id].quantity, 2)

        cart.remove_product(product.id)
        self.assertTrue(cart.is_empty())

    def test_customer_can_cancel_order(self):
        user = self.auth_service.register("cancel_buyer", "12345")
        product = self.product_service.add_product("Наушники", "Аудио", 3000, 5)
        cart = Cart()
        cart.add_product(product, 2)

        order = self.order_service.create_order(user.id, cart, self.product_service.get_all())
        cancelled_order = self.order_service.cancel_order_by_user(order.id, user.id)

        self.assertEqual(cancelled_order.status, "cancelled")
        restored_product = self.product_service.get_by_id(product.id)
        self.assertEqual(restored_product.quantity, 5)


if __name__ == "__main__":
    unittest.main()
