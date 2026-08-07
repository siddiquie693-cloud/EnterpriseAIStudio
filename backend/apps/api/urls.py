from django.urls import include, path

from .views import HealthCheckAPIView

urlpatterns = [
    path("health/", HealthCheckAPIView.as_view(), name="health"),
    path(
        "auth/",
        include("apps.users.urls"),
    ),
]
