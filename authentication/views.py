import logging

import requests
from django.conf import settings
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ROLE_STAFF
from .permissions import IsAdmin
from .serializers import (
    ChangePasswordSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare the token request
        token_url = "http://localhost:8000/o/token/"
        data = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "client_id": settings.OAUTH2_CLIENT_ID,
            "client_secret": settings.OAUTH2_CLIENT_SECRET,
        }

        # Make the request for a token
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return Response(
                {"error": "Failed to get token"}, status=response.status_code
            )

        return Response(response.json())


class CustomTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RefreshTokenSerializer)
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = refresh.access_token
                return Response(
                    {
                        "access": str(new_access_token),
                        "refresh": str(refresh),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {
                        "detail": str(e)
                    },  # This will provide the specific error from the token library
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateStaffView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        request.data["role"] = ROLE_STAFF
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Staff account created successfully.",
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = AccessToken.objects.get(token=request.auth)
            token.revoke()  # Revoke the access token
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except AccessToken.DoesNotExist:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )
