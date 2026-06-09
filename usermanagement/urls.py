from django.urls import path
from django.views.generic import TemplateView

from .views import CustomPasswordResetView, PostOnlyLogoutView, signup

urlpatterns = [
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        TemplateView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    # Project-specific account routes only (built-in auth URLs are included globally)
    path("signup/", signup, name="signup"),
    path("logout/", PostOnlyLogoutView.as_view(), name="logout"),
    # Keep a direct URL for the pending-signup confirmation page
    path(
        "signup/pending/",
        TemplateView.as_view(template_name="registration/signup_pending.html"),
        name="signup_pending",
    ),
]
