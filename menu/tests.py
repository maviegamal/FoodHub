import shutil
import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from core.testing import ApiTestCase, image_file
from menu.models import Food

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class FoodTests(ApiTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def payload(self, **over):
        data = {
            "name": "Falafel Plate",
            "cuisine": "Middle Eastern",
            "description": "Crispy falafel with tahini.",
            "price": "7.50",
            "rating": "4.5",
            "is_available": "true",
            "image": image_file(),
        }
        data.update(over)
        return data

    def create(self, **over):
        return self.client.post("/api/admin/foods/", self.payload(**over))

    def test_public_menu_hides_unavailable(self):
        self.login("boss")
        self.create(name="Visible")
        self.create(name="Hidden", is_available="false")
        self.client.post("/api/auth/logout/")
        names = [f["name"] for f in self.client.get("/api/foods/").json()["foods"]]
        self.assertEqual(names, ["Visible"])

    def test_admin_creates_food_with_image(self):
        self.login("boss")
        res = self.create()
        self.assertEqual(res.status_code, 201)
        food = res.json()["food"]
        self.assertTrue(food["image"].startswith("/media/foods/"))
        self.assertEqual(food["price"], "7.50")

    def test_normal_user_and_anonymous_cannot_manage_food(self):
        self.assertEqual(self.create().status_code, 401)
        self.login("alice")
        self.assertEqual(self.create().status_code, 403)
        self.assertEqual(Food.objects.count(), 0)

    def test_validation_errors(self):
        self.login("boss")
        res = self.create(price="-1", name="")
        self.assertEqual(res.status_code, 422)
        fields = res.json()["fields"]
        self.assertIn("price", fields)
        self.assertIn("name", fields)
        self.assertIn("rating", self.create(rating="9").json()["fields"])

    def test_image_required_on_create(self):
        self.login("boss")
        data = self.payload()
        del data["image"]
        res = self.client.post("/api/admin/foods/", data)
        self.assertIn("image", res.json()["fields"])

    def test_rejects_non_image_upload(self):
        self.login("boss")
        fake = SimpleUploadedFile("evil.png", b"<script>alert(1)</script>", content_type="image/png")
        res = self.create(image=fake)
        self.assertEqual(res.status_code, 422)
        self.assertIn("image", res.json()["fields"])

    def test_rejects_oversized_image(self):
        self.login("boss")
        # A valid PNG larger than 2 MB, built from random noise.
        import os
        from io import BytesIO
        from PIL import Image

        noise = Image.frombytes("RGB", (1000, 1000), os.urandom(1000 * 1000 * 3))
        buf = BytesIO()
        noise.save(buf, "PNG")
        self.assertGreater(buf.tell(), 2 * 1024 * 1024)
        upload = SimpleUploadedFile("noise.png", buf.getvalue(), content_type="image/png")
        res = self.create(image=upload)
        self.assertEqual(res.status_code, 422)
        self.assertIn("2 MB", res.json()["fields"]["image"])

    def test_update_keeps_image_when_not_replaced_and_replaces_when_sent(self):
        self.login("boss")
        food = self.create().json()["food"]
        data = self.payload(name="Falafel Deluxe")
        del data["image"]
        res = self.client.post(f"/api/admin/foods/{food['id']}/", data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["food"]["name"], "Falafel Deluxe")
        self.assertEqual(res.json()["food"]["image"], food["image"])

        res = self.client.post(f"/api/admin/foods/{food['id']}/", self.payload(image=image_file("new.png")))
        self.assertNotEqual(res.json()["food"]["image"], food["image"])

    def test_delete_food(self):
        self.login("boss")
        food = self.create().json()["food"]
        self.assertEqual(self.client.delete(f"/api/admin/foods/{food['id']}/").status_code, 200)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(self.client.delete(f"/api/admin/foods/{food['id']}/").status_code, 404)
