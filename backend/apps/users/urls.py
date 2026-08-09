from django.urls import path

from .views import (
    ChangePasswordAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserProfileAPIView,
    UserRefreshTokenAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    path(
        "register/",
        UserRegistrationAPIView.as_view(),
        name="user-register",
    ),
    path(
        "login/",
        UserLoginAPIView.as_view(),
        name="user-login",
    ),
    path(
        "refresh/",
        UserRefreshTokenAPIView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        UserLogoutAPIView.as_view(),
        name="user-logout",
    ),
    path(
        "profile/",
        UserProfileAPIView.as_view(),
        name="user-profile",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
]
