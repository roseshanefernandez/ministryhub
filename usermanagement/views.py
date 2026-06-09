from django.contrib.auth import get_user_model
from django.contrib.auth.views import LogoutView, PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm

User = get_user_model()


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Create user and show a confirmation/pending page instead of auto-login
            user.is_active = False
            user.save()

            return render(
                request,
                "registration/signup_pending.html",
                {"username": form.cleaned_data.get("username")},
            )
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/reset_password.html"
    success_url = reverse_lazy("password_reset_done")


class PostOnlyLogoutView(LogoutView):
    """Custom logout view that only accepts POST requests for security and renders a confirmation page."""

    http_method_names = ["post"]
    template_name = "registration/logout.html"
