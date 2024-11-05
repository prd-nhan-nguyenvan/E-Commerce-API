from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import CustomUser
from users.models import UserProfile


class ProfileUpdateTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", username="testuser", password="testpassword"
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)

        self.url = reverse("profile-detail")

    def test_patch_update_profile(self):
        """Test partial update (PATCH) for the user's profile"""
        data = {
            "first_name": "NewName",
            "last_name": "NewLastName",
            "bio": "Updated bio",
        }

        response = self.client.patch(self.url, data, format="multipart")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.first_name, "NewName")
        self.assertEqual(self.profile.last_name, "NewLastName")
        self.assertEqual(self.profile.bio, "Updated bio")

        self.assertEqual(self.profile.user.email, "testuser@example.com")
        self.assertEqual(self.profile.user.role, self.user.role)

    def test_put_update_profile(self):
        """Test full update (PUT) for the user's profile"""
        data = {
            "first_name": "FullNewName",
            "last_name": "FullNewLastName",
            "bio": "Completely updated bio",
            "phone_number": "0987654321",
            "address": "New Address",
        }

        response = self.client.put(self.url, data, format="multipart")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.first_name, "FullNewName")
        self.assertEqual(self.profile.last_name, "FullNewLastName")
        self.assertEqual(self.profile.bio, "Completely updated bio")
        self.assertEqual(self.profile.phone_number, "0987654321")
        self.assertEqual(self.profile.address, "New Address")

        self.assertEqual(self.profile.user.email, "testuser@example.com")
        self.assertEqual(self.profile.user.role, self.user.role)

    def test_upload_image(self):
        """Test uploading a profile picture"""

        image = Image.new("RGB", (100, 100), color="red")
        img_io = BytesIO()
        image.save(img_io, format="JPEG")
        img_io.seek(0)

        image_file = SimpleUploadedFile(
            name="test_image.jpg", content=img_io.read(), content_type="image/jpeg"
        )

        data = {
            "profile_picture": image_file,
            "first_name": "NewNameWithImage",
            "last_name": "NewLastNameWithImage",
        }

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, "NewNameWithImage")
        self.assertEqual(self.profile.last_name, "NewLastNameWithImage")
        self.assertIsNotNone(self.profile.profile_picture)
        self.assertEqual(self.profile.profile_picture.name[-3:], "jpg")

    def test_unauthorized_access(self):
        """Test unauthorized access to the profile update endpoint."""
        # Ensure the user is logged out
        self.client.logout()

        data = {
            "first_name": "UnauthorizedName",
            "last_name": "UnauthorizedLastName",
        }

        response = self.client.patch(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_read_only_fields(self):
        data = {
            "user": self.user.id,
            "role": "admin",
        }

        response = self.client.patch(self.url, data, format="multipart")

        # The status code should be 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Instead of checking for 'user' and 'role', check for the error message
        self.assertIn("You cannot update read-only fields.", str(response.data))
