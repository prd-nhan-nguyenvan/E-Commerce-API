# tests/test_user_detail.py in your users app

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authentication.models import CustomUser


class UserDetailTest(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com",
            username="adminuser",
            password="adminpassword",
            role="admin",
        )
        self.regular_user = CustomUser.objects.create_user(
            email="user@example.com",
            username="regularuser",
            password="userpassword",
            role="user",
        )
        self.client.force_authenticate(user=self.admin_user)
        self.url = reverse("user-detail", [self.regular_user.id])

    def test_get_user_detail(self):
        """Test getting user details."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.regular_user.email)

    def test_block_user(self):
        """Test blocking a user."""
        response = self.client.patch(self.url, data={"action": "block"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_unblock_user(self):
        """Test unblocking a user."""
        # First block the user
        self.regular_user.is_blocked = True
        self.regular_user.save()

        response = self.client.patch(self.url, data={"action": "unblock"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_active)
