import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("token_refresh")


@pytest.mark.django_db
def test_token_refresh(api_client, url, user, application):
    data = {"email": user.email, "password": "testpassword"}
    response = api_client.post(reverse("token_obtain_pair"), data, format="json")
    data = {"refresh": response.data["refresh_token"]}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.data
    assert "refresh_token" in response.data


@pytest.mark.django_db
def test_token_refresh_missing_refresh_token(api_client, url):
    data = {}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "refresh" in response.data


@pytest.mark.django_db
def test_token_refresh_invalid_refresh_token(api_client, url):
    data = {"refresh": "invalid_refresh_token"}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "RefreshToken matching query does not exist."


@pytest.mark.django_db
def test_token_refresh_serializer_error(api_client, url):
    data = {"refresh": None}

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "refresh" in response.data
