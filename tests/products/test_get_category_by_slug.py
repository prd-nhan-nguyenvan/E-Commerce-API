import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def category_url(category):
    return reverse("category-detail-by-slug", kwargs={"slug": category.slug})


@pytest.mark.django_db
def test_get_category_by_slug(api_client, category, category_url):
    response = api_client.get(category_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == category.name


@pytest.mark.django_db
def test_get_category_by_slug_not_found(api_client):
    url = reverse("category-detail-by-slug", kwargs={"slug": "non-existent-slug"})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "No Category matches the given query."
