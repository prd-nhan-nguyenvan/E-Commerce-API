import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import ROLE_STAFF
from .helper import custom_token_generator
from .permissions import IsAdmin
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            # Authenticate the user
            user = authenticate(email=email, password=password)
            if not user:
                return Response(
                    {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )

            application = Application.objects.get(client_id=settings.OAUTH2_CLIENT_ID)
            expires = now() + timedelta(
                seconds=settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]
            )
            access_token = AccessToken.objects.create(
                user=user,
                application=application,
                token=custom_token_generator(),
                expires=expires,
                scope="read write",
            )
            refresh_token = RefreshToken.objects.create(
                user=user,
                token=custom_token_generator(),  # Automatically generate the refresh token
                access_token=access_token,
                application=application,
            )

            response_data = {
                "access_token": access_token.token,
                "expires_in": settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"],
                "token_type": "Bearer",
                "scope": "read write",
                "refresh_token": refresh_token.token,
            }

            return Response(data=response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
