from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from products.models import Category, Product, Review

User = get_user_model()


class ProductReviewListViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@gmail.com",
            username="testuser",
            password="testpass",
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            category_id=self.category.pk,
            name="Organic Coconut Oil",
            description="Cold-pressed, organic coconut oil with a subtle coconut flavor.",
            price="12.99",
            sell_price="11.99",
            on_sell=False,
            stock=200,
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product!",
        )
        self.url = reverse("product-reviews", kwargs={"product_id": self.product.id})

    def test_list_reviews(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["comment"], "Great product!")

    def test_create_review(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "product": self.product.id,
            "rating": 4,
            "comment": "Good product!",
        }

        response = self.client.post(reverse("create-review"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment"], "Good product!")

    def test_create_review_without_rating(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "product": self.product.id,
            "comment": "Good product!",
        }

        response = self.client.post(reverse("create-review"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["rating"][0], "This field is required.")

    def test_create_review_without_comment(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "product": self.product.id,
            "rating": 4,
        }

        response = self.client.post(reverse("create-review"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
