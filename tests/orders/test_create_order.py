from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from orders.models import Order, OrderItem, Product
from products.models import Category
from users.models import UserProfile

User = get_user_model()


class OrderListCreateViewTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@gmail.com"
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

        self.url = reverse("order-list-create")

    def test_get_order_list(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.order.id)

    def test_get_order_list_filtered_by_status(self):

        response = self.client.get(self.url, {"status": "pd"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(self.url, {"status": "cp"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_order_with_items(self):

        data = {
            "address": "456 New St",
            "items": [
                {"product": self.product1.id, "quantity": 1},
                {"product": self.product2.id, "quantity": 2},
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.address, "456 New St")
        self.assertEqual(order.items.count(), 2)

        total_price = sum(
            item.quantity * item.price_at_purchase for item in order.items.all()
        )
        self.assertEqual(response.data["total_price"], total_price)

    def test_create_order_with_missing_address(self):

        data = {
            "items": [
                {"product": self.product1.id, "quantity": 1},
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.address, self.user_profile.address)

    def test_create_order_with_insufficient_stock(self):

        data = {
            "address": "456 New St",
            "items": [
                {
                    "product": self.product1.id,
                    "quantity": 101,
                },
            ],
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "Not enough stock for Product 1.",
        )
