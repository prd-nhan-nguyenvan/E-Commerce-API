from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from orders.models import Order, OrderItem, Product
from products.models import Category
from users.models import UserProfile

User = get_user_model()


class ChangeOrderStatusTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@gmail.com"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpass", email="otheruser@gmail.com"
        )
        self.user_profile = UserProfile.objects.filter(user=self.user).first()
        self.user_profile.address = "123 Main St"
        self.user_profile.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Category 1")

        self.product1 = Product.objects.create(
            name="Product 1",
            price="10.0",
            sell_price="9.5",
            stock=100,
            category=self.category,
            description="Product 1 description",
            on_sell=False,
        )

        self.product2 = Product.objects.create(
            name="Product 2",
            price="20.0",
            sell_price="18.5",
            stock=50,
            category=self.category,
            description="Product 2 description",
            on_sell=False,
        )

        self.order = Order.objects.create(
            user=self.user, address="123 Test St", status="pd"
        )
        OrderItem.objects.create(
            order=self.order, product=self.product1, quantity=2, price_at_purchase=10.0
        )

        self.url = reverse("update-order-status", args=[self.order.id])

    def test_update_order_status_success(self):

        data = {"status": "sb"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order"]["status"], "sb")

    def test_update_order_status_invalid_transition(self):

        data = {"status": "cp"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_invalid_status_value(self):

        data = {"status": "invalid_status"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_another_user(self):

        self.client.logout()
        self.client.force_authenticate(user=self.other_user)
        data = {"status": "sb"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status_unauthenticated(self):

        self.client.logout()
        data = {"status": "sb"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
