from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from .models import UserProfile
from .serializers import UserProfileSerializer


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    @swagger_auto_schema(tags=["User"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=["User"])
    def put(self, request, *args, **kwargs):
        # For a full update, ensure the user field remains unchanged
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["User"])
    def patch(self, request, *args, **kwargs):
        # Ensure user cannot update the `user` field directly
        return super().partial_update(request, *args, **kwargs)
