import pytest
from rest_framework.test import APIClient

from authentication.models import CustomUser
from products.factories import CategoryFactory, ProductFactory


@pytest.fixture
def api_client():
    """Fixture for setting up an API client."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Fixture for creating an admin user."""
    return CustomUser.objects.create_superuser(
        email="admintest@gmail.com",
        username="adminuser",
        password="adminpassword",
    )


@pytest.fixture
def regular_user(db):
    """Fixture for creating a regular user."""
    return CustomUser.objects.create_user(
        email="nonAdmin@gmail.com",
        username="nonadminuser",
        password="nonadminpassword",
    )


@pytest.fixture
def setup_categories(api_client, admin_user):
    """Fixture for setting up categories."""
    CategoryFactory(name="Category 1")
    CategoryFactory(name="Category 2")
    CategoryFactory(name="Category 3")
    CategoryFactory(name="Category 4")


@pytest.fixture
def setup_products(api_client, admin_user):
    """Fixture for setting up products."""
    ProductFactory(name="Product 1")
    ProductFactory(name="Product 2")
    ProductFactory(name="Product 3")
    ProductFactory(name="Product 4")


@pytest.fixture
def product_data(category):
    """Fixture for creating product data."""
    return dict(
        {
            "category": category.pk,
            "name": "Test Product",
            "description": "Test Description",
            "price": "9.99",
            "sell_price": "8.99",
            "on_sell": True,
            "stock": 100,
        }
    )


@pytest.fixture
def category():
    """Fixture for creating a category with a factory."""
    return CategoryFactory(name="Test Category")


@pytest.fixture
def product(category):
    return ProductFactory(name="Test Product", category=category)


@pytest.fixture
def mock_bulk_import(mocker):
    return mocker.patch("products.tasks.bulk_import_products.delay")
