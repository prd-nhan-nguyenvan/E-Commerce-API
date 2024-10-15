from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "role",
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "profile_picture",
            "phone_number",
            "address",
        ]
        read_only_fields = ["user", "role"]

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        validated_data.pop("role", None)

        return super().update(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "role", "is_active", "date_joined"]


class UserSupportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "bio",
            "profile_picture",
            "phone_number",
            "address",
        ]
        read_only_fields = ["user", "role"]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserSupportDetailSerializer(source="userprofile", read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_active",
            "date_joined",
            "is_active",
            "date_joined",
            "last_login",
            "profile",
        ]  # Include any other user fields you need
