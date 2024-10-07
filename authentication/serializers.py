from django.contrib.auth.password_validation import validate_password
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import serializers

from .constants import ROLE_USER
from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "role"]
        read_only_fields = ["role"]

    def __init__(self, *args, **kwargs):
        self.role = kwargs.pop("role", ROLE_USER)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        validated_data["role"] = self.role
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def validate(self, data):
        self.validate_old_password(data["old_password"])
        return data

    def save(self):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        AccessToken.objects.filter(user=user).delete()
        RefreshToken.objects.filter(user=user).delete()

        return user


class LogoutSerializer(serializers.Serializer):
    pass
