from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework import generics, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.constants import ROLE_STAFF, ROLE_USER
from authentication.helper import custom_token_generator
from authentication.permissions import IsAdmin
from authentication.serializers import (
    ChangePasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={201: LoginResponseSerializer, 400: "Invalid credentials"},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

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
                token=custom_token_generator(),
                access_token=access_token,
                application=application,
            )

            response_data = LoginResponseSerializer(
                data={
                    "access_token": access_token.token,
                    "expires_in": settings.OAUTH2_PROVIDER[
                        "ACCESS_TOKEN_EXPIRE_SECONDS"
                    ],
                    "token_type": "Bearer",
                    "scope": "read write",
                    "refresh_token": refresh_token.token,
                }
            )

            if response_data.is_valid():
                return Response(data=response_data.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    response_data.errors, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RefreshTokenSerializer)
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)

        if serializer.is_valid():
            refresh_token_value = serializer.validated_data.get("refresh")
            if not refresh_token_value:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:

                refresh_token = RefreshToken.objects.get(token=refresh_token_value)

                if not refresh_token.access_token:
                    return Response(
                        {"detail": "Invalid refresh token."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                expires = now() + timedelta(
                    seconds=settings.OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]
                )
                new_access_token = AccessToken.objects.create(
                    user=refresh_token.user,
                    application=refresh_token.application,
                    token=custom_token_generator(),
                    expires=expires,
                    scope=refresh_token.access_token.scope,
                )

                response_data = {
                    "access_token": new_access_token.token,
                    "expires_in": settings.OAUTH2_PROVIDER[
                        "ACCESS_TOKEN_EXPIRE_SECONDS"
                    ],
                    "token_type": "Bearer",
                    "scope": "read write",
                    "refresh_token": refresh_token.token,
                }

                return Response(
                    response_data,
                    status=status.HTTP_200_OK,
                )

            except RefreshToken.DoesNotExist:
                return Response(
                    {"detail": "Invalid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(request_body=RegisterSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, role=ROLE_USER)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "User created successfully"}, status=status.HTTP_201_CREATED
        )


class CreateStaffView(CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(request_body=RegisterSerializer)
    def create(self, request):
        serializer = self.get_serializer(data=request.data, role=ROLE_STAFF)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "message": "Staff account created successfully.",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = request.auth.token
            access_token = AccessToken.objects.get(token=token)
            refresh_token = RefreshToken.objects.filter(
                access_token=access_token
            ).first()

            if refresh_token:
                refresh_token.revoke()

            access_token.delete()

            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except AccessToken.DoesNotExist:
            return Response(
                {"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
