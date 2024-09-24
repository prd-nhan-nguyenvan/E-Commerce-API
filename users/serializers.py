from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "bio",
            "profile_picture",
            "phone_number",
            "address",
        ]
        read_only_fields = ["user"]
