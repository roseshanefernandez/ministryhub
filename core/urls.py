# main urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from usermanagement.views import CustomLoginView  # 1. Import it here

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirect bare /accounts/ to the login page
    path(
        "accounts/",
        RedirectView.as_view(url="/accounts/login/", permanent=False),
        name="accounts-root-redirect",
    ),
    # 2. Force your custom view to match first at the root level
    path(
        "accounts/login/",
        CustomLoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    # Project-specific account routes (signup, POST-only logout, logout success)
    path("accounts/", include("usermanagement.urls")),
    # Built-in Django auth routes (login, password change/reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    # MinistryHub
    path("ministryhub/", include("ministryhub.urls")),
    # Site pages
    path("", include("portfolio.urls")),
]
