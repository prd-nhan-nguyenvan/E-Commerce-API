import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.fixture
def url():
    return reverse("change_password")


@pytest.mark.django_db
def test_change_password_success(api_client, user, url):
    data = {"old_password": "testpassword", "new_password": "newsecurepassword123"}

    api_client.force_authenticate(user=user)
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Password updated successfully."

    user.refresh_from_db()
    assert user.check_password("newsecurepassword123")


@pytest.mark.django_db
def test_change_password_incorrect_old_password(api_client, user, url):
    data = {"old_password": "incorrectpassword", "new_password": "newsecurepassword123"}

    api_client.force_authenticate(user=user)
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "old_password" in response.data


@pytest.mark.django_db
def test_change_password_new_password_validation(api_client, user, url):
    data = {"old_password": "testpassword", "new_password": "short"}

    api_client.force_authenticate(user=user)
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password" in response.data


@pytest.mark.django_db
def test_change_password_unauthorized(api_client, url):
    data = {"old_password": "testpassword", "new_password": "newsecurepassword123"}

    api_client.logout()
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
