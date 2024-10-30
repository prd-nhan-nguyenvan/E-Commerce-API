from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserProfile

User = get_user_model()


class ProfileRetrieveTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", username="testuser", password="testpassword"
        )
        self.client = self.client_class()
        self.client.force_authenticate(user=self.user)

        self.url = reverse("profile-detail")

    def test_retrieve_profile(self):
        """Test retrieving the user's profile."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = UserProfile.objects.get(user=self.user)

        self.assertEqual(response.data["first_name"], profile.first_name)
        self.assertEqual(response.data["last_name"], profile.last_name)
        self.assertEqual(response.data["bio"], profile.bio)
        self.assertEqual(response.data["phone_number"], profile.phone_number)
        self.assertEqual(response.data["role"], self.user.role)

    def test_unauthenticated_user_cannot_access_profile(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
