from django.urls import path

from authentication.views import ChangePasswordView

from .views import ProfileRetrieveUpdateView

urlpatterns = [
    path("profile/", ProfileRetrieveUpdateView.as_view(), name="profile-detail"),
    path("password/change/", ChangePasswordView.as_view(), name="change_password"),
]
