from io import BytesIO

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("bulk-import-products")


@pytest.mark.django_db
def test_bulk_import_no_file_provided(api_client, url, mock_bulk_import, admin_user):

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, {})

    # Assert that the response is 400 when no file is provided
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "No file provided."


@pytest.mark.django_db
def test_bulk_import_with_valid_file(api_client, url, mock_bulk_import, admin_user):
    csv_file = BytesIO(
        b"name,description,price,sell_price,on_sell,stock,category_name,image_url\nProduct1,Description1,10,9,1,100,Category1,https://example.com/image1.jpg\nProduct2,Description2,20,18,0,200,Category2,https://example.com/image2.jpg"
    )
    csv_file.name = "products.csv"

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, {"file": csv_file}, format="multipart")

    assert response.status_code == status.HTTP_202_ACCEPTED
    mock_bulk_import.assert_called_once()


@pytest.mark.django_db
def test_bulk_import_with_invalid_csv(api_client, url, mock_bulk_import, admin_user):
    invalid_csv_file = BytesIO(
        b"name,description\nProduct1,Description1\nProduct2,Description2"
    )
    invalid_csv_file.name = "invalid_products.csv"

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, {"file": invalid_csv_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
