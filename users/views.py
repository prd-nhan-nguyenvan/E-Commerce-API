from rest_framework import generics, permissions

from .models import UserProfile
from .serializers import UserProfileSerializer


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        # For a full update, ensure the user field remains unchanged
        return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # Ensure user cannot update the `user` field directly
        return super().partial_update(request, *args, **kwargs)
