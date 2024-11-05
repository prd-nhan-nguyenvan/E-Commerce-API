import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.fixture
def profile_url():
    """Fixture for profile detail URL."""
    return reverse("profile-detail")


@pytest.mark.django_db
class TestProfileRetrieve:
    def test_retrieve_profile(self, api_client, user, user_profile, profile_url):
        """Test retrieving the user's profile."""
        api_client.force_authenticate(user=user)
        response = api_client.get(profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == user_profile.first_name
        assert response.data["last_name"] == user_profile.last_name
        assert response.data["bio"] == user_profile.bio
        assert response.data["phone_number"] == user_profile.phone_number
        assert response.data["role"] == user.role

    def test_unauthenticated_user_cannot_access_profile(self, api_client, profile_url):
        """Test that an unauthenticated user cannot access the profile."""
        response = api_client.get(profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
