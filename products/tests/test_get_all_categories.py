from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import CustomUser


class CategoryListTest(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            email="admintest@gmail.com",
            username="adminuser",
            password="adminpassword",
        )

        # add some categories
        self.client.force_authenticate(user=self.admin_user)
        self.client.post(
            reverse("category-list-create"),
            data={"name": "Category 1", "description": "Description 1"},
        )
        self.client.post(
            reverse("category-list-create"),
            data={"name": "Category 2", "description": "Description 2"},
        )
        self.client.post(
            reverse("category-list-create"),
            data={"name": "Category 3", "description": "Description 3"},
        )
        self.client.post(
            reverse("category-list-create"),
            data={"name": "Category 4", "description": "Description 4"},
        )

        self.client = self.client_class()

        self.url = reverse("category-list-create")

    def test_admin_can_create_category(self):
        """Test that an admin user can create a category."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, data={"name": "Test Category"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Category")

    def test_non_admin_cannot_create_category(self):
        """Test that a non-admin user cannot create a category."""
        regular_user = CustomUser.objects.create_user(
            email="nonAdmin@gmail.com",
            username="nonadminuser",
            password="nonadminpassword",
        )
        self.client.force_authenticate(user=regular_user)
        response = self.client.post(self.url, data={"name": "Test Category"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_categories(self):
        """Test that an admin user can get the list of all categories."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data[0]["name"], "Category 1")
        self.assertEqual(response.data[1]["name"], "Category 2")
        self.assertEqual(response.data[2]["name"], "Category 3")
        self.assertEqual(response.data[3]["name"], "Category 4")
