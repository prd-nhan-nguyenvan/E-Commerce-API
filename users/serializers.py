from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "role",
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
