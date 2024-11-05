import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url():
    return reverse("profile-detail")


@pytest.mark.django_db
class TestProfileUpdate:
    def test_profile_update(self, api_client, user_profile, url, user):
        data = {
            "first_name": "NewName",
            "last_name": "NewLastName",
            "bio": "Updated bio",
        }

        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK

        user_profile.refresh_from_db()
        assert user_profile.first_name == data["first_name"]
        assert user_profile.last_name == data["last_name"]
        assert user_profile.bio == data["bio"]
        assert user_profile.user.email == "testuser@example.com"
        assert user_profile.user.role == user.role

    def test_unauthenticated_user_cannot_update_profile(self, api_client, url):
        data = {
            "first_name": "NewName",
            "last_name": "NewLastName",
            "bio": "Updated bio",
        }

        response = api_client.patch(url, data, format="multipart")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_profile_update_with_invalid_data(
        self, api_client, user_profile, url, user
    ):
        data = {
            "first_name": "",
            "last_name": "NewLastName",
            "bio": "Updated bio",
            "phone_number": "1234567890",
        }

        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["first_name"][0] == "This field may not be blank."
