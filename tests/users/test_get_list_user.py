import pytest
from rest_framework.reverse import reverse


@pytest.fixture
def url():
    return reverse("user-list")


@pytest.mark.django_db
class TestUserList:
    def test_admin_can_list_users(self, api_client, admin_user, user, url):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["email"] == user.email
        assert response.data["results"][1]["email"] == admin_user.email

    def test_non_admin_cannot_list_users(self, api_client, user, url):
        api_client.force_authenticate(user=user)
        response = api_client.get(url)

        assert response.status_code == 403

    def test_unauthenticated_user_cannot_list_users(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == 401
