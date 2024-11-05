from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ChangePasswordViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        cls.application = Application.objects.create(
            name="Test Application",
            client_id=settings.OAUTH2_CLIENT_ID,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        cls.url = reverse("change_password")

    def setUp(self):
        # Get access token for the user
        self.token_url = reverse("token_obtain_pair")
        response = self.client.post(
            self.token_url,
            {"email": "testuser@example.com", "password": "testpassword"},
        )
        self.access_token = response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_change_password_success(self):
        data = {"old_password": "testpassword", "new_password": "newsecurepassword123"}
        response = self.client.patch(self.url, data)
        self.user.refresh_from_db()  # Refresh the user instance
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.check_password("newsecurepassword123"))

    def test_change_password_incorrect_old_password(self):
        data = {"old_password": "wrongpassword", "new_password": "newsecurepassword123"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["old_password"], ["Old password is not correct."]
        )

    def test_change_password_new_password_validation(self):
        data = {
            "old_password": "testpassword",
            "new_password": "short",  # New password is too short
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)  # Ensure error is in response

    def test_change_password_unauthorized(self):
        self.client.logout()  # Log out the user
        data = {"old_password": "testpassword", "new_password": "newsecurepassword123"}
        response = self.client.patch(self.url, data)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # Should be forbidden
