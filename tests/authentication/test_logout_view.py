import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("logout")


@pytest.mark.django_db
def test_successful_logout(api_client, user, url, application):
    data = {"email": user.email, "password": "testpassword"}
    response = api_client.post(reverse("token_obtain_pair"), data, format="json")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access_token']}")

    response = api_client.post(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not response.data
    assert not response.cookies


@pytest.mark.django_db
def test_logout_with_invalid_access_token(api_client, url):
    # Use an invalid token
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
    response = api_client.post(url)

    # Check response status
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.django_db
def test_logout_without_authentication(api_client, url):
    response = api_client.post(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
