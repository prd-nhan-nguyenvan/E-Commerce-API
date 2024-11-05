from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from carts.serializers import CartSerializer


@pytest.fixture
def url():
    return reverse("get-cart")


@pytest.mark.django_db
class TestGetCartView:
    def test_get_cart_from_cache(self, api_client, user, cart, url):
        with patch("django.core.cache.cache.get") as mock_cache_get, patch(
            "django.core.cache.cache.set"
        ):

            serializer = CartSerializer(cart)
            mock_cache_get.return_value = serializer.data
            api_client.force_authenticate(user=user)

            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            mock_cache_get.assert_called_with(f"user_cart_{user.id}")

            assert response.data == serializer.data

    def test_get_cart_from_db_and_cache(self, api_client, user, cart, url):
        with patch("django.core.cache.cache.get") as mock_cache_get, patch(
            "django.core.cache.cache.set"
        ) as mock_cache_set:

            mock_cache_get.return_value = None
            api_client.force_authenticate(user=user)

            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            mock_cache_set.assert_called_with(
                f"user_cart_{user.id}", response.data, timeout=60 * 5
            )

            serializer = CartSerializer(cart)
            assert response.data == serializer.data

    def test_get_cart_unauthenticated(self, api_client, url):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
