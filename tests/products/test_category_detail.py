import pytest
from django.urls import reverse
from rest_framework import status

from products.models import Category


@pytest.fixture
def category_url(category):
    """Fixture to generate the URL for the category detail."""
    return reverse("category-detail", args=[category.pk])


@pytest.mark.django_db
def test_get_category_detail(api_client, admin_user, category, category_url):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(category_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == category.name


@pytest.mark.django_db
def test_put_category_detail(api_client, admin_user, category_url):
    api_client.force_authenticate(user=admin_user)
    data = {"name": "New Category"}
    response = api_client.put(category_url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_patch_category_detail(api_client, admin_user, category_url):
    api_client.force_authenticate(user=admin_user)
    data = {"name": "New Category"}
    response = api_client.patch(category_url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_delete_category_detail(api_client, admin_user, category, category_url):
    api_client.force_authenticate(user=admin_user)
    response = api_client.delete(category_url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Category.objects.count() == 0


@pytest.mark.django_db
def test_non_admin_cannot_delete_category(
    api_client, regular_user, category, category_url
):
    api_client.force_authenticate(user=regular_user)
    response = api_client.delete(category_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Category.objects.count() == 1
