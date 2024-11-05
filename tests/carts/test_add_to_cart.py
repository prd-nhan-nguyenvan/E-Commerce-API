import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from carts.models import Cart, CartItem


@pytest.fixture
def url():
    return reverse("add-to-cart")


@pytest.mark.django_db
def test_add_item_to_cart_success(api_client, user, product, url):
    api_client.force_authenticate(user=user)
    data = {"product_id": product.id, "quantity": 2}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Item added to cart successfully"
    assert response.data["cart_item"]["quantity"] == 2

    cart = Cart.objects.get(user=user)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    assert cart_item.quantity == 2

    cache_key = f"user_cart_{user.id}"
    assert cache.get(cache_key) is None


@pytest.mark.django_db
def test_add_item_exceeds_stock(api_client, user, product, url):
    api_client.force_authenticate(user=user)
    data = {"product_id": product.id, "quantity": 20}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"Only {product.stock} items in stock." in response.data["non_field_errors"]


@pytest.mark.django_db
def test_unauthenticated_user_cannot_add_to_cart(api_client, product, url):
    api_client.logout()

    data = {"product_id": product.id, "quantity": 2}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_existing_cart_item_quantity(api_client, user, product, url):
    api_client.force_authenticate(user=user)
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=3)

    data = {"product_id": product.id, "quantity": 2}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["cart_item"]["quantity"] == 5

    cart_item.refresh_from_db()
    assert cart_item.quantity == 5

    cache_key = f"user_cart_{user.id}"
    assert cache.get(cache_key) is None
