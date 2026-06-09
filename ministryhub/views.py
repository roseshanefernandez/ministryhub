from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, DetailView
from django.views import View
from django.http import JsonResponse
from ministryhub.models import BibleVerse, Event

from .forms import ProfileForm
from .models import Profile, Announcement

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "ministryhub/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = None

        try:
            # Set the desired timezone using zoneinfo
            desired_timezone = ZoneInfo(settings.TIME_ZONE)  # Use TIME_ZONE from settings
            # Get the current time in the desired timezone
            today_in_timezone = timezone.localtime(
                timezone.now(), timezone=desired_timezone
            ).date()
            daily_verse = BibleVerse.objects.get(date=today_in_timezone)
        except BibleVerse.DoesNotExist:
            daily_verse = None

        # Get top 5 upcoming events (nearest dates in the future)
        today = timezone.now().date()
        upcoming_events = Event.objects.filter(end_date__gte=today, closed=False).order_by(
            "start_date"
        )[:5]

        announcements = Announcement.objects.filter(active=True).order_by("-created_at")

        context["announcements"] = announcements
        context["profile"] = profile
        context["show_profile_modal"] = profile is None
        context["upcoming_events"] = upcoming_events
        context["verse"] = daily_verse

        if not profile:
            context["form"] = ProfileForm(
                self.request.POST if self.request.method == "POST" else None,
                request_user=self.request.user,
            )
        return context


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = "ministryhub/profile_detail.html"
    model = Profile
    context_object_name = "profile"

    def get(self, request, *args, **kwargs):
        # 1. Determine if we are looking for 'self' or a specific ID
        profile_id = self.kwargs.get("id")
        
        # 2. Attempt to fetch the profile object
        if profile_id is None:
            # Fallback to logged-in user's profile
            try:
                self.object = request.user.profile
            except Profile.DoesNotExist:
                self.object = None
        else:
            # Look up specific profile by ID
            self.object = Profile.objects.filter(id=profile_id).first()

        # 3. Redirect to dashboard if no profile exists
        if not self.object:
            return redirect(reverse("ministryhub:dashboard"))

        # 4. Profile exists: proceed with standard template rendering
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class CreateProfileView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = "ministryhub/create_profile.html"

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user  # Associate profile with logged-in user
        profile.save()
        return redirect("ministryhub:my_profile")


class MemberProfilesView(LoginRequiredMixin, TemplateView):
    template_name = "ministryhub/member_profiles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profiles"] = Profile.objects.all().order_by("first_name", "last_name")
        return context


class MemberProfileDetailAjaxView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=pk)

        data = {
            "id": profile.id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "birthday": profile.birthday.isoformat() if profile.birthday else None,
            "gender": profile.gender,
            "facebook_page": profile.facebook_page,
            "ministry": profile.ministry,
            "priority_ministry": profile.priority_ministry,
        }

        # Include user email if available
        if profile.user and hasattr(profile.user, "email"):
            data["email"] = profile.user.email

        # Include spouse info if present
        if profile.spouse:
            data["spouse_id"] = profile.spouse.id
            data["spouse_name"] = f"{profile.spouse.first_name} {profile.spouse.last_name}"

        return JsonResponse(data)
