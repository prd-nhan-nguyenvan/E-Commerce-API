from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.helper import custom_token_generator

User = get_user_model()

# Setting the expires field to a valid datetime
expires = timezone.now() + timedelta(days=1)  # Set to 1 day from now


class LogoutViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )
        cls.application = Application.objects.create(
            name="Test Application",
            client_id=settings.OAUTH2_CLIENT_ID,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        cls.token = custom_token_generator()
        # Create access and refresh tokens for the user
        cls.access_token = AccessToken.objects.create(
            user=cls.user, expires=expires, application=cls.application, token=cls.token
        )
        cls.refresh_token = RefreshToken.objects.create(
            user=cls.user, access_token=cls.access_token, application=cls.application
        )
        cls.logout_url = reverse("logout")  # Update with your actual URL name

    def test_successful_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token.token}")
        response = self.client.post(self.logout_url)

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Successfully logged out"})

        # Check if the access token is deleted
        self.assertFalse(
            AccessToken.objects.filter(token=self.access_token.token).exists()
        )

        # Check if the refresh token is revoked
        self.assertTrue(self.refresh_token)

    def test_logout_with_invalid_access_token(self):
        # Use an invalid token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = self.client.post(self.logout_url)

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("not_authenticated", response.data["detail"].code)

    def test_logout_without_authentication(self):
        response = self.client.post(self.logout_url)

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        # Cleanup any objects created during tests
        User.objects.all().delete()
        Application.objects.all().delete()
        AccessToken.objects.all().delete()
        RefreshToken.objects.all().delete()
