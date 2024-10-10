from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status
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

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["email", "is_active"]  # Fields to filter by
    search_fields = ["email", "username"]  # You can search by email
    ordering_fields = ["email", "date_joined"]
    ordering = ["-date_joined"]  # Default

    def get(self, request, *args, **kwargs):
        default_limit = getattr(settings, "DEFAULT_LIMIT", 10)
        default_offset = getattr(settings, "DEFAULT_OFFSET", 0)

        limit = request.query_params.get("limit", default_limit)
        offset = request.query_params.get("offset", default_offset)

        filters_data = request.query_params.dict()  # All query params for cache key
        cache_key = f"user_list_{limit}_{offset}_{filters_data}"

        cached_users = cache.get(cache_key)

        if cached_users:
            return Response(cached_users, status=status.HTTP_200_OK)

        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)  # Cache for 1 hour
        return response


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        cache_key = f"user_detail_{user_id}"

        # Check if the data is in the cache
        cached_user = cache.get(cache_key)
        if cached_user:
            return Response(cached_user, status=status.HTTP_200_OK)

        # If not, retrieve the user from the database
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)  # Cache for 1 hour
        return response

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        action = request.data.get("action")

        if action == "block":
            user.is_active = False
            user.save()

        elif action == "unblock":
            user.is_active = True
            user.save()

        # Clear cache after updating the user
        cache_key = f"user_detail_{user.id}"
        cache.delete(cache_key)

        return super().patch(request, *args, **kwargs)
