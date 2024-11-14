import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def url(user):
    return reverse("user-detail", args=[user.id])


@pytest.mark.django_db
class TestUserDetail:
    def test_get_user_detail(self, api_client, admin_user, user, url):
        """Test getting user details."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_non_admin_cannot_get_user_detail(self, api_client, user, url):
        api_client.force_authenticate(user=user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_block_user(self, api_client, admin_user, user, url):
        """Test blocking a user."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(url, data={"action": "block"})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert not user.is_active

    def test_unauthenticated_user_cannot_block_user(self, api_client, user, url):
        api_client.logout()

        response = api_client.patch(url, data={"action": "block"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_cannot_block_user(self, api_client, user, url):
        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data={"action": "block"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unblock_user(self, api_client, admin_user, user, url):
        """Test unblocking a user."""
        # First block the user
        user.is_blocked = True
        user.save()

        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(url, data={"action": "unblock"})

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active

    def test_non_admin_cannot_unblock_user(self, api_client, user, url):
        api_client.force_authenticate(user=user)
        response = api_client.patch(url, data={"action": "unblock"})

        assert response.status_code == status.HTTP_403_FORBIDDEN
