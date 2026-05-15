from django.contrib.auth.views import LogoutView
from django.shortcuts import render

from .forms import CustomUserCreationForm


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # New accounts must be inactive until an admin enables them
            user.is_active = False
            user.save()
            # Do NOT auto-login inactive users; show a confirmation message instead
            return render(
                request, "registration/signup_pending.html", {"username": user.username}
            )
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


class PostOnlyLogoutView(LogoutView):
    """Custom logout view that only accepts POST requests for security and renders a confirmation page."""

    http_method_names = ["post"]
    template_name = "registration/logout.html"


from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.shortcuts import render


class CustomLoginView(LoginView):
    def form_invalid(self, form):
        # 1. Extract credentials entered by the user
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        if username and password:
            User = get_user_model()
            try:
                # 2. Look up the user matching the identifier
                # Use username or email depending on your User model configuration
                user = User.objects.get(username=username)
                # 3. If password matches but user is inactive, intercept the workflow
                if user.check_password(password) and not user.is_active:
                    return render(
                        self.request,
                        "registration/signup_pending.html",
                        {"username": user.username},
                    )
            except User.DoesNotExist:
                pass  # Fall back to standard invalid error for non-existent users

        # 4. If it's a standard bad password, proceed with normal error rendering
        return super().form_invalid(form)
