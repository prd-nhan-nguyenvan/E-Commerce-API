from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LoginViewTestCase(APITestCase):
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
        cls.url = reverse("token_obtain_pair")

    @patch("django.contrib.auth.authenticate")
    @patch("authentication.helper.custom_token_generator")
    def test_successful_login(self, mock_custom_token_generator, mock_authenticate):
        mock_authenticate.return_value = self.user

        data = {"email": "testuser@example.com", "password": "testpassword"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertEqual(response.data["token_type"], "Bearer")
        self.assertEqual(response.data["scope"], "read write")
        self.assertEqual(
            response.data["expires_in"],
            settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"],
        )
        self.assertTrue(AccessToken.objects.filter(user=self.user).exists())
        self.assertTrue(RefreshToken.objects.filter(user=self.user).exists())

    @patch("django.contrib.auth.authenticate")
    def test_login_invalid_credentials(self, mock_authenticate):
        mock_authenticate.return_value = None
        data = {"email": "invaliduser@example.com", "password": "invalidpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_login_missing_email(self):
        data = {"password": "testpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_missing_password(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_invalid_email_format(self):
        data = {"email": "invalid_email_format", "password": "testpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def tearDown(self):
        User.objects.all().delete()
        Application.objects.all().delete()
        AccessToken.objects.all().delete()
        RefreshToken.objects.all().delete()
