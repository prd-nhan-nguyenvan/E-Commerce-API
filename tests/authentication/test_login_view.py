from unittest.mock import patch

import pytest
from django.conf import settings
from django.urls import reverse
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import status


@pytest.fixture
def url():
    return reverse("token_obtain_pair")


@pytest.mark.django_db
@patch("django.contrib.auth.authenticate")
@patch("authentication.helper.custom_token_generator")
def test_successful_login(
    mock_custom_token_generator, mock_authenticate, api_client, user, url, application
):

    data = {"email": "testuser@example.com", "password": "testpassword"}
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.data
    assert "refresh_token" in response.data
    assert response.data["token_type"] == "Bearer"
    assert response.data["scope"] == "read write"
    assert (
        response.data["expires_in"]
        == settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]
    )
    assert AccessToken.objects.filter(user=user).exists()
    assert RefreshToken.objects.filter(user=user).exists()


@patch("django.contrib.auth.authenticate")
@pytest.mark.django_db
def test_login_invalid_credentials(mock_authenticate, api_client, url):
    mock_authenticate.return_value = None
    data = {"email": "invaliduser@example.com", "password": "invalidpassword"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid credentials"


def test_login_missing_email(api_client, url):
    data = {"password": "testpassword"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_login_missing_password(api_client, url):
    data = {"email": "testuser@example.com"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


def test_invalid_email_format(api_client, url):
    data = {"email": "invalid_email_format", "password": "testpassword"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
