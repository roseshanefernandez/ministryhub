from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from ministryhub.models import BibleVerse, Event

from .forms import ProfileForm
from .models import Profile


@login_required
def dashboard(request):
    """Main dashboard view with profile info and upcoming events carousel."""
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    try:
        daily_verse = BibleVerse.objects.get(date=timezone.now().date())
    except BibleVerse.DoesNotExist:
        daily_verse = None

    # Get top 5 upcoming events (nearest dates in the future)
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(end_date__gte=today, closed=False).order_by(
        "start_date"
    )[:5]

    print(upcoming_events)
    context = {
        "profile": profile,
        "show_profile_modal": profile is None,
        "upcoming_events": upcoming_events,
        "verse": daily_verse,
    }

    if not profile:
        context["form"] = ProfileForm(request.POST, request_user=request.user)

    return render(request, "ministryhub/dashboard.html", context)


@login_required
def profile_detail(request):
    """Show the authenticated user's Profile. If missing, redirect to creation page."""
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return redirect(reverse("ministryhub:dashboard"))

    context = {"profile": profile}
    return render(request, "ministryhub/profile_detail.html", context)


@login_required
def create_profile(request):

    if request.method == "POST":

        form = ProfileForm(request.POST, request_user=request.user)

        if form.is_valid():

            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return redirect("ministryhub:profile")
    return redirect("ministryhub:dashboard")
