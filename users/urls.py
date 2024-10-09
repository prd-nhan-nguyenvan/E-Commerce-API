from django.urls import path

from authentication.views import ChangePasswordView

from .views import ProfileRetrieveUpdateView, UserDetailView, UserListView

urlpatterns = [
    path("profile/", ProfileRetrieveUpdateView.as_view(), name="profile-detail"),
    path("password/change/", ChangePasswordView.as_view(), name="change_password"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
