from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from authentication.permissions import IsAdmin

from .models import UserProfile
from .serializers import UserDetailSerializer, UserListSerializer, UserProfileSerializer


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    @swagger_auto_schema(tags=["User"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["User"])
    def put(self, request, *args, **kwargs):
        self.validate_update_fields(request.data)
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["User"])
    def patch(self, request, *args, **kwargs):
        self.validate_update_fields(request.data)
        return super().partial_update(request, *args, **kwargs)

    def validate_update_fields(self, data):
        if "user" in data or "role" in data:
            raise ValidationError("You cannot update read-only fields.")
        return data


class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdmin]  # Only admin users can access this view

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        action = request.data.get("action")

        if action == "block":
            user.is_active = False
            user.save()
            return Response(
                {"detail": "User blocked successfully."}, status=status.HTTP_200_OK
            )

        elif action == "unblock":
            user.is_active = True
            user.save()
            return Response(
                {"detail": "User unblocked successfully."}, status=status.HTTP_200_OK
            )

        return super().patch(request, *args, **kwargs)
