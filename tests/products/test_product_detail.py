import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from products.models import Product


@pytest.fixture
def url(product):
    return reverse("product-detail", kwargs={"pk": product.pk})


@pytest.fixture
def product_by_slug_url(product):
    return reverse("product-detail-by-slug", kwargs={"slug": product.slug})


@pytest.mark.django_db
class TestProductDetail:
    def test_get(self, api_client, url, product):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == product.name
        assert response.data["description"] == product.description

    def test_put(
        self, api_client, url, product, product_data, admin_user, mock_edited_image
    ):
        data = product_data
        data["name"] = "new name"
        data["description"] = "new description"
        data["image"] = mock_edited_image
        api_client.force_authenticate(user=admin_user)
        response = api_client.put(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK

        product.refresh_from_db()
        assert response.data["name"] == data["name"]
        assert response.data["description"] == data["description"]

    def test_invalid_put(self, api_client, url, admin_user):
        data = {"price": -100}
        api_client.force_authenticate(user=admin_user)
        response = api_client.put(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data
        assert response.data["price"] == ["Price cannot be negative."]

    def test_patch(self, api_client, url, product, admin_user):
        data = {"name": "Updated name"}
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == "Updated name"

    def test_delete(self, api_client, url, product, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_non_admin_cannot_delete_product(
        self, api_client, url, product, regular_user
    ):
        api_client.force_authenticate(user=regular_user)
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Product.objects.filter(pk=product.pk).exists()

    def test_get_product_by_slug(self, api_client, product, product_by_slug_url):
        response = api_client.get(product_by_slug_url)

        assert response.status_code == status.HTTP_200_OK

        assert response.data["name"] == product.name
