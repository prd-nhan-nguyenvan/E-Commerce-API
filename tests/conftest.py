import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from products.models import Category, Product

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com", password="testpassword", username="user"
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admintest@gmail.com", username="adminuser", password="adminpassword"
    )


@pytest.fixture
def mock_image():
    image = Image.new("RGB", (100, 100), color="red")
    image_file = io.BytesIO()
    image.save(image_file, format="JPEG")
    image_file.seek(0)

    return SimpleUploadedFile(
        "test_image.jpg", image_file.read(), content_type="image/jpeg"
    )


@pytest.fixture
def mock_edited_image():
    image = Image.new("RGB", (100, 100), color="blue")
    image_file = io.BytesIO()
    image.save(image_file, format="JPEG")
    image_file.seek(0)

    return SimpleUploadedFile(
        "test_edited_image.jpg", image_file.read(), content_type="image/jpeg"
    )


@pytest.fixture
def category(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(
        reverse("category-list"),
        data={"name": "Groceries", "description": "Grocery items"},
    )
    return Category.objects.get(id=response.data["id"])


@pytest.fixture
def product(api_client, admin_user, category, mock_image):

    api_client.force_authenticate(user=admin_user)

    product_response = api_client.post(
        reverse("product-list"),
        data={
            "category": category.pk,
            "name": "Organic Extra Virgin Olive Oil",
            "description": "Cold-pressed, organic olive oil with a rich and fruity flavor.",
            "price": "15.99",
            "sell_price": "14.99",
            "on_sell": True,
            "stock": 10,
            "image": mock_image,
        },
    )
    return Product.objects.get(id=product_response.data["id"])
