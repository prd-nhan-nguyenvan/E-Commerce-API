import pytest
from django.urls import reverse

from carts.models import Cart


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)


@pytest.fixture
def add_product_to_cart(api_client, user, product):
    api_client.force_authenticate(user=user)
    data = {"product_id": product.id, "quantity": 2}
    api_client.post(reverse("add-to-cart"), data, format="json")
    return reverse("update-remove-from-cart", args=[product.id])
