from uuid import uuid4

from django.contrib.auth import get_user_model
from django.urls import reverse
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CustomTokenRefreshViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user()
        cls.application = cls.create_application()
        cls.refresh_token = RefreshToken.objects.create(
            token="valid_refresh_token",
            user=cls.user,
            application=cls.application,
        )

        cls.url = reverse("token_refresh")

    @classmethod
    def create_user(cls):
        username = f"testuser-{uuid4()}"
        return get_user_model().objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpassword",
        )

    @classmethod
    def create_application(cls):
        from oauth2_provider.models import Application

        return Application.objects.create(
            user=cls.create_user(),
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            name="Test Application",
        )

    def test_token_refresh_missing_refresh_token(self):
        data = {}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

    def test_token_refresh_invalid_refresh_token(self):
        data = {"refresh": "invalid_refresh_token"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid refresh token.")

    def test_token_refresh_serializer_error(self):
        data = {"refresh": None}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

    def tearDown(self):
        User.objects.all().delete()
        Application.objects.all().delete()
        AccessToken.objects.all().delete()
        RefreshToken.objects.all().delete()
