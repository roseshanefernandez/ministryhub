from django.urls import path

from .prayer_views import PrayerRequestsView
from .views import (
    CreateProfileView,
    DashboardView,
    MemberProfileDetailAjaxView,
    MemberProfilesView,
    ProfileDetailView,
)

app_name = "ministryhub"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileDetailView.as_view(), name="my_profile"),
    path("profile/<int:id>/", ProfileDetailView.as_view(), name="user_profile"),
    path("profile/create/", CreateProfileView.as_view(), name="create_profile"),
    path("members/", MemberProfilesView.as_view(), name="member_profiles"),
    path(
        "members/profile/<int:pk>/",
        MemberProfileDetailAjaxView.as_view(),
        name="member_profile_detail",
    ),
    path("prayer-requests/", PrayerRequestsView.as_view(), name="prayer_requests"),
]
