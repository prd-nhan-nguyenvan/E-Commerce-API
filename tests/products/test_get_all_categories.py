import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_admin_can_create_category(api_client, admin_user):
    """Test that an admin user can create a category."""
    api_client.force_authenticate(user=admin_user)
    url = reverse("category-list")
    response = api_client.post(url, data={"name": "Test Category"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test Category"


@pytest.mark.django_db
def test_non_admin_cannot_create_category(api_client, regular_user):
    """Test that a non-admin user cannot create a category."""
    api_client.force_authenticate(user=regular_user)
    url = reverse("category-list")
    response = api_client.post(url, data={"name": "Test Category"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_all_categories(api_client, admin_user, setup_categories):
    """Test that an admin user can get the list of all categories."""
    api_client.force_authenticate(user=admin_user)
    url = reverse("category-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 4
    assert response.data["results"][0]["name"] == "Category 1"
