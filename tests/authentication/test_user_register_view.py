import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("register")


@pytest.mark.django_db
def test_register_user_success(api_client, url, clear_users):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"message": "User created successfully"}


@pytest.mark.django_db
def test_register_user_empty_username(api_client, url, clear_users):
    data = {
        "username": "",
        "email": "valid.email@example.com",
        "password": "validPassword123",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data


@pytest.mark.django_db
def test_register_user_invalid_email(api_client, url, clear_users):
    data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "validPassword123",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_register_user_short_password(api_client, url, clear_users):
    data = {
        "username": "testuser",
        "email": "valid.email@example.com",
        "password": "123",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data
