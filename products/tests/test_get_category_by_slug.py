from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.factories import CategoryFactory


class GetCategoryBySlugTests(APITestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.url = reverse(
            "category-detail-by-slug", kwargs={"slug": self.category.slug}
        )

    def test_get_category_by_slug(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)
        self.assertEqual(response.data["description"], self.category.description)

    def test_get_category_by_slug_not_found(self):
        url = reverse("category-detail-by-slug", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No Category matches the given query."
        )
