# conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from carts.models import Cart

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="testuser@gmail.com", username="testuser", password="testpass"
    )


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)
