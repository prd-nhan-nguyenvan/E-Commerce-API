from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.constants import ROLE_STAFF

User = get_user_model()


class CreateStaffViewTest(APITestCase):
    def setUp(self):
        # Create an admin user to authorize the request
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )

        # URL for staff registration
        self.url = reverse(
            "register_staff"
        )  # 'register_staff' should match the name in your urlpatterns

        # Admin credentials to authenticate
        self.client.force_authenticate(user=self.admin_user)

    def test_staff_registration_success(self):
        # Test data for valid staff registration
        data = {
            "username": "staffuser",
            "email": "staff@example.com",
            "password": "password123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"], "Staff account created successfully."
        )

        # Verify that the user is created with the ROLE_STAFF role
        user = User.objects.get(username="staffuser")
        self.assertEqual(user.role, ROLE_STAFF)

    def test_password_too_short(self):
        # Invalid data (missing email, invalid password)
        data = {
            "email": "staff@gmail.com",
            "username": "staffuser",
            "password": "123",  # Too short
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)  # Check for password error (too short)

    def test_staff_registration_unauthorized(self):
        # Log out admin and use a normal user
        self.client.logout()

        # Create a regular user
        user = User.objects.create_user(
            username="normaluser", email="user@example.com", password="userpass"
        )

        # Force authenticate with the normal user
        self.client.force_authenticate(user=user)

        # Attempt to register a staff account
        data = {
            "username": "staffuser",
            "email": "staff@example.com",
            "password": "password123",
        }

        response = self.client.post(self.url, data, format="json")

        # Check that the normal user cannot create a staff account (unauthorized)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
