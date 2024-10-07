from django.urls import path

from .views import (
    CreateStaffView,
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "register/staff/",
        CreateStaffView.as_view(),
        name="register_staff",
    ),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
