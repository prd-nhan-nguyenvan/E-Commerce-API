import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("product-list-create")


@pytest.mark.django_db
def test_admin_can_create_product(api_client, admin_user, product_data, url):
    data = product_data
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == data["name"]
    assert response.data["description"] == data["description"]
    assert response.data["price"] == data["price"]
    assert response.data["sell_price"] == data["sell_price"]
    assert response.data["category"] == data["category"]


@pytest.mark.django_db
def test_non_admin_cannot_create_product(api_client, regular_user, product_data, url):
    data = product_data

    api_client.force_authenticate(user=regular_user)
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_all_products(api_client, admin_user, setup_products, url):

    api_client.force_authenticate(user=admin_user)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 4
    assert response.data["results"][0]["name"] == "Product 4"
    assert response.data["results"][1]["name"] == "Product 3"
    assert response.data["results"][2]["name"] == "Product 2"
    assert response.data["results"][3]["name"] == "Product 1"
