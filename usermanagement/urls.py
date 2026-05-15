from django.urls import path

from .views import PostOnlyLogoutView, signup

urlpatterns = [
    # Project-specific account routes only (built-in auth URLs are included globally)
    path("signup/", signup, name="signup"),
    path("logout/", PostOnlyLogoutView.as_view(), name="logout"),
]
