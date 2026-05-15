from django.urls import path

from .views import create_profile, dashboard, profile_detail

app_name = "ministryhub"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    # Intentional route spelling per request: 'profile/'
    path("profile/", profile_detail, name="profile"),
    path("profile/create/", create_profile, name="create_profile"),
]
