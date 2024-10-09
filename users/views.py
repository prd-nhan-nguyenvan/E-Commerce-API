from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser

from authentication.permissions import IsAdmin

from .models import UserProfile
from .serializers import UserListSerializer, UserProfileSerializer


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
