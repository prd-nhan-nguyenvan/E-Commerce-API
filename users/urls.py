from django.urls import path

from .views import ProfileRetrieveUpdateView

urlpatterns = [
    path("profile/", ProfileRetrieveUpdateView.as_view(), name="profile-detail"),
]
