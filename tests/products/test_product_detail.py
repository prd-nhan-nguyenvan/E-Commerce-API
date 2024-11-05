from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import CustomUser
from products.models import Category, Product


class ProductDetailTest(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            email="admintest@gmail.com",
            username="adminuser",
            password="adminpassword",
        )

        self.client.force_authenticate(user=self.admin_user)

        self.category = Category.objects.create(name="Test Category")
        self.product = self.client.post(
            reverse("product-list-create"),
            data={
                "category": self.category.pk,
                "name": "Organic Extra Virgin Olive Oil",
                "description": "Cold-pressed, organic olive oil with a rich and fruity flavor.",
                "price": "15.99",
                "sell_price": "14.99",
                "on_sell": True,
                "stock": 300,
            },
        )

        self.url = reverse("product-detail", args=[self.product.data["id"]])
        self.data = {
            "category": self.category.pk,
            "name": "Organic Coconut Oil",
            "description": "Cold-pressed, organic coconut oil with a subtle coconut flavor.",
            "price": "12.99",
            "sell_price": "11.99",
            "on_sell": False,
            "stock": 200,
        }

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Organic Extra Virgin Olive Oil")

    def test_put(self):
        response = self.client.put(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.data["name"])

    def test_patch(self):
        response = self.client.patch(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.data["name"])

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_non_admin_cannot_delete(self):
        regular_user = CustomUser.objects.create_user(
            email="noadmin@gmail.com",
            username="noadminuser",
            password="noadminpassword",
        )
        self.client.force_authenticate(user=regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)
