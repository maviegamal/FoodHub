import shutil
import tempfile
from decimal import Decimal

from django.test import override_settings

from core.testing import PASSWORD, ApiTestCase, User, image_file
from menu.models import Food
from orders.models import Order

TEMP_MEDIA = tempfile.mkdtemp()
ADDRESS = {"address": "12 Nile Street, Banha", "phone": "+20 100 123 4567", "note": ""}


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class OrderTests(ApiTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.pizza = self.make_food("Pizza", "10.00")
        self.soup = self.make_food("Soup", "4.25")
        self.bob = User.objects.create_user("bob", "bob@example.com", PASSWORD)

    def make_food(self, name, price, available=True):
        food = Food(name=name, cuisine="Test", description="d", price=Decimal(price), is_available=available)
        food.image.save("x.png", image_file(), save=False)
        food.save()
        return food

    def add(self, food, quantity=1):
        return self.post_json("/api/cart/", {"food_id": food.id, "quantity": quantity})

    # ---- cart ----
    def test_cart_requires_login_and_rejects_admin(self):
        self.assertEqual(self.client.get("/api/cart/").status_code, 401)
        self.login("boss")
        self.assertEqual(self.client.get("/api/cart/").status_code, 403)
        self.assertEqual(self.add(self.pizza).status_code, 403)

    def test_add_update_remove(self):
        self.login("alice")
        self.add(self.pizza, 2)
        res = self.add(self.pizza, 1)
        cart = res.json()["cart"]
        self.assertEqual(cart["count"], 3)
        self.assertEqual(cart["total"], "30.00")

        res = self.put_json(f"/api/cart/items/{self.pizza.id}/", {"quantity": 1})
        self.assertEqual(res.json()["cart"]["total"], "10.00")
        self.assertEqual(self.put_json(f"/api/cart/items/{self.pizza.id}/", {"quantity": 0}).status_code, 422)
        self.assertEqual(self.put_json(f"/api/cart/items/{self.pizza.id}/", {"quantity": 999}).status_code, 422)

        res = self.client.delete(f"/api/cart/items/{self.pizza.id}/")
        self.assertEqual(res.json()["cart"]["items"], [])

    def test_quantity_is_capped(self):
        self.login("alice")
        self.add(self.pizza, 20)
        self.assertEqual(self.add(self.pizza, 5).json()["cart"]["count"], 20)

    def test_cannot_add_unavailable_or_missing_or_bad_input(self):
        hidden = self.make_food("Hidden", "1.00", available=False)
        self.login("alice")
        self.assertEqual(self.add(hidden).status_code, 404)
        self.assertEqual(self.post_json("/api/cart/", {"food_id": 9999}).status_code, 404)
        self.assertEqual(self.post_json("/api/cart/", {"food_id": "abc"}).status_code, 422)
        self.assertEqual(self.post_json("/api/cart/", {"food_id": self.pizza.id, "quantity": -3}).status_code, 422)

    def test_carts_are_private(self):
        self.login("alice")
        self.add(self.pizza)
        self.client.post("/api/auth/logout/")
        self.login("bob")
        self.assertEqual(self.client.get("/api/cart/").json()["cart"]["items"], [])
        self.assertEqual(self.client.delete(f"/api/cart/items/{self.pizza.id}/").status_code, 404)

    # ---- checkout ----
    def test_checkout_uses_server_prices_and_clears_cart(self):
        self.login("alice")
        self.add(self.pizza, 2)
        self.add(self.soup, 1)
        res = self.post_json("/api/orders/", {**ADDRESS, "total": "0.01"})  # client total ignored
        self.assertEqual(res.status_code, 201)
        order = res.json()["order"]
        self.assertEqual(order["total"], "24.25")
        self.assertEqual(order["status"], "pending")
        self.assertEqual(len(order["items"]), 2)
        self.assertEqual(self.client.get("/api/cart/").json()["cart"]["count"], 0)

        # Later price change does not change the old order.
        self.pizza.price = Decimal("99.00")
        self.pizza.save()
        self.assertEqual(self.client.get("/api/orders/").json()["orders"][0]["total"], "24.25")

    def test_checkout_validation(self):
        self.login("alice")
        self.assertEqual(self.post_json("/api/orders/", ADDRESS).status_code, 400)  # empty cart
        self.add(self.pizza)
        res = self.post_json("/api/orders/", {"address": "x", "phone": "abc"})
        self.assertEqual(res.status_code, 422)
        self.assertIn("address", res.json()["fields"])
        self.assertIn("phone", res.json()["fields"])
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_blocks_unavailable_items(self):
        self.login("alice")
        self.add(self.pizza)
        self.pizza.is_available = False
        self.pizza.save()
        res = self.post_json("/api/orders/", ADDRESS)
        self.assertEqual(res.status_code, 409)
        self.assertEqual(Order.objects.count(), 0)

    def test_orders_are_private_and_cancel_rules(self):
        self.login("alice")
        self.add(self.pizza)
        order_id = self.post_json("/api/orders/", ADDRESS).json()["order"]["id"]
        self.client.post("/api/auth/logout/")

        self.login("bob")
        self.assertEqual(self.client.get("/api/orders/").json()["orders"], [])
        self.assertEqual(self.post_json(f"/api/orders/{order_id}/cancel/").status_code, 404)
        self.client.post("/api/auth/logout/")

        self.login("alice")
        res = self.post_json(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(res.json()["order"]["status"], "cancelled")
        self.assertEqual(self.post_json(f"/api/orders/{order_id}/cancel/").status_code, 409)

    # ---- admin ----
    def test_admin_order_flow_and_permissions(self):
        self.login("alice")
        self.add(self.pizza)
        order_id = self.post_json("/api/orders/", ADDRESS).json()["order"]["id"]
        self.assertEqual(self.client.get("/api/admin/orders/").status_code, 403)
        self.assertEqual(self.post_json(f"/api/admin/orders/{order_id}/status/", {"status": "delivered"}).status_code, 403)
        self.client.post("/api/auth/logout/")

        self.login("boss")
        res = self.client.get("/api/admin/orders/")
        self.assertEqual(res.json()["orders"][0]["username"], "alice")
        self.assertEqual(self.post_json(f"/api/admin/orders/{order_id}/status/", {"status": "delivered"}).status_code, 409)
        self.assertEqual(self.post_json(f"/api/admin/orders/{order_id}/status/", {"status": "bogus"}).status_code, 422)
        for status in ["preparing", "out_for_delivery", "delivered"]:
            res = self.post_json(f"/api/admin/orders/{order_id}/status/", {"status": status})
            self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["order"]["next_statuses"], [])

    def test_admin_stats(self):
        self.login("alice")
        self.add(self.pizza, 2)
        self.post_json("/api/orders/", ADDRESS)
        self.client.post("/api/auth/logout/")
        self.login("boss")
        stats = self.client.get("/api/admin/stats/").json()
        self.assertEqual(stats["users"], 2)  # alice + bob (admin not counted)
        self.assertEqual(stats["orders"], 1)
        self.assertEqual(stats["revenue"], "20.00")
        self.assertEqual(stats["foods"], 2)
