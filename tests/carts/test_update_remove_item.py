import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_update_item_from_cart_success(api_client, user, product, add_product_to_cart):
    api_client.force_authenticate(user=user)
    data = {"quantity": 2}
    response = api_client.patch(add_product_to_cart, data, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_remove_item_from_cart_success(api_client, user, product, add_product_to_cart):
    api_client.force_authenticate(user=user)
    response = api_client.delete(add_product_to_cart)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_remove_item_from_cart_failure(api_client, user, product):
    api_client.force_authenticate(user=user)
    invalid_url = reverse("update-remove-from-cart", args=[product.id + 1])
    response = api_client.delete(invalid_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
