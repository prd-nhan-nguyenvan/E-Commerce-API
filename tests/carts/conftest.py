# conftest.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Product

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="user@example.com", password="testpassword", username="user"
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admintest@gmail.com", username="adminuser", password="adminpassword"
    )


@pytest.fixture
def product(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    category_response = api_client.post(
        reverse("category-list-create"),
        data={"name": "Category 1", "description": "Description 1"},
    )
    product_response = api_client.post(
        reverse("product-list-create"),
        data={
            "category": category_response.data["id"],
            "name": "Organic Extra Virgin Olive Oil",
            "description": "Cold-pressed, organic olive oil with a rich and fruity flavor.",
            "price": "15.99",
            "sell_price": "14.99",
            "on_sell": True,
            "stock": 10,
        },
    )
    return Product.objects.get(id=product_response.data["id"])
