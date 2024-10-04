from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_user_success(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "User created successfully"})

    def test_register_user_empty_username(self):
        data = {
            "username": "",
            "email": "valid.email@example.com",
            "password": "validPassword123",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_user_invalid_email(self):
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "validPassword123",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # TODO:  HANDLE THIS FEATURE TO CHECK THE STRONG PASSWORD
    # def test_register_user_short_password(self):
    #     pass
    #     data = {
    #         "username": "testuser",
    #         "email": "valid.email@example.com",
    #         "password": "123",
    #     }
    #     response = self.client.post(self.url, data, format="json")
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("password", response.data)

    def tearDown(self):
        User.objects.all().delete()
