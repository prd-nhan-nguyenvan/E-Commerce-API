from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import CustomUser
from products.models import Category


class CategoryDetailTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.url = reverse("category-detail", args=[self.category.pk])
        self.data = {"name": "New Category"}

        self.admin_user = CustomUser.objects.create_superuser(
            email="admintest@gmail.com",
            username="adminuser",
            password="adminpassword",
        )

        # add some categories
        self.client.force_authenticate(user=self.admin_user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

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
        self.assertEqual(Category.objects.count(), 0)

    def test_non_admin_cannot_delete(self):
        regular_user = CustomUser.objects.create_user(
            email="noadmin@gmail.com",
            username="noadminuser",
            password="noadminpassword",
        )
        self.client.force_authenticate(user=regular_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 1)
