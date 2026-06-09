# main urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirect bare /accounts/ to the login page
    path(
        "accounts/",
        RedirectView.as_view(url="/accounts/login/", permanent=False),
        name="accounts-root-redirect",
    ),
    # App routes for signup/logout; built-in auth provides login and password management.
    path("accounts/", include("usermanagement.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    # MinistryHub
    path("ministryhub/", include("ministryhub.urls")),
    # Site pages
    path("", include("portfolio.urls")),
    path("portfolio", include("portfolio.urls")),
]
