import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("register_staff")


@pytest.mark.django_db
def test_register_user_success(api_client, url, clear_users, admin_user):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
    }

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Staff account created successfully."


@pytest.mark.django_db
def test_register_user_empty_username(api_client, url, clear_users, admin_user):
    data = {
        "username": "",
        "email": "valid.email@example.com",
        "password": "validPassword123",
    }

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data


@pytest.mark.django_db
def test_register_user_invalid_email(api_client, url, clear_users, admin_user):
    data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "validPassword123",
    }

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_register_user_short_password(api_client, url, clear_users, admin_user):
    data = {
        "username": "testuser",
        "email": "valid.email@example.com",
        "password": "123",
    }

    api_client.force_authenticate(user=admin_user)

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


@pytest.mark.django_db
def test_register_user_without_admin_permission(api_client, url, clear_users, user):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
    }

    api_client.force_authenticate(user=user)

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        response.data["detail"] == "You do not have permission to perform this action."
    )
