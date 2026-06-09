"""
Prayer Requests Views
Location: ministryhub/prayer_views.py

Separate module for prayer request views to keep code organized.
"""

from collections import defaultdict
from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import TemplateView

from .models import PrayerRequest

# ============================================
# PRAYER REQUEST CATEGORIES
# ============================================

# Matches PRAYER_CATEGORY_CHOICES from models.py
PRAYER_CATEGORY_DISPLAY = {
    "Thanksgiving": "Thanksgiving",
    "Healing and Good Health": "Healing and Good Health",
    "Souls": "Souls",
    "Safety and Protection": "Safety and Protection",
    "Financial Abundance": "Financial Abundance",
    "Guidance and Protection": "Guidance and Protection",
    "Special Intentions": "Special Intentions",
}


class PrayerRequestsView(LoginRequiredMixin, TemplateView):
    """
    View for displaying prayer requests for the current month and week.
    Only displays active prayer requests.

    Context Variables:
    - current_month: Current month name
    - current_week: Current week number
    - prayer_categories: List of all prayer category choices
    - prayer_requests_by_category: Dict of prayer requests grouped by category
    - prayer_requests: Flat list of all active prayers for current month/week
    """

    template_name = "ministryhub/prayer_requests.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get current month, week, and year
        today = date.today()
        current_month = today.strftime("%B")
        current_week = self._get_current_week(today)
        current_year = today.year

        # Get active prayer requests for current month and week
        active_prayers = self._get_active_prayers(
            current_month, current_week, current_year
        )

        # Group prayers by category
        prayers_by_category = self._group_by_category(active_prayers)

        # Add to context
        context.update(
            {
                "current_month": current_month,
                "current_week": current_week,
                "current_year": current_year,
                "prayer_categories": self._get_prayer_categories(),
                "prayer_requests": active_prayers,
                "prayer_requests_by_category": prayers_by_category,
                "has_prayers": bool(active_prayers),
            }
        )

        return context

    # ============================================
    # HELPER METHODS
    # ============================================

    @staticmethod
    def _get_current_week(target_date=None) -> int:
        """
        Calculate the current week number of the month.

        Week 1: Days 1-7
        Week 2: Days 8-14
        Week 3: Days 15-21
        Week 4: Days 22-28
        Week 5: Days 29+

        Args:
            target_date: Optional date object. Defaults to today.

        Returns:
            int: Week number (1-5)
        """
        if target_date is None:
            target_date = date.today()

        # Get the first day of the month
        first_day = target_date.replace(day=1)

        # Calculate week: (day + weekday offset) / 7, rounded up
        week = ((target_date.day + first_day.weekday() - 1) // 7) + 1

        # Clamp between 1 and 5
        return min(max(week, 1), 5)

    @staticmethod
    def _get_active_prayers(month: str, week: int, year: int) -> QuerySet:
        """
        Retrieve active prayer requests for the specified month and week.

        Args:
            month: Month name (e.g., 'January', 'February')
            week: Week number (1-5)
            year: Year (e.g., 2026)

        Returns:
            QuerySet: Filtered and ordered prayer requests
        """
        return PrayerRequest.objects.filter(
            month=month, week=week, year=year, is_active=True
        ).order_by("category", "-created_at")

    @staticmethod
    def _group_by_category(prayers: QuerySet) -> dict:
        """
        Group prayer requests by their category.

        Args:
            prayers: QuerySet of prayer requests

        Returns:
            dict: Dictionary with categories as keys and lists of prayers as values
        """
        grouped = defaultdict(list)

        for prayer in prayers:
            grouped[prayer.category].append(prayer)

        return dict(grouped)

    @staticmethod
    def _get_prayer_categories() -> list:
        """
        Get all prayer categories for display.
        Returns categories in the same order as PRAYER_CATEGORY_CHOICES in models.py

        Returns:
            list: List of tuples (code, display_name)
        """
        return [
            (
                "Thanksgiving",
                PRAYER_CATEGORY_DISPLAY.get("Thanksgiving", "Thanksgiving"),
            ),
            (
                "Healing and Good Health",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Healing and Good Health", "Healing and Good Health"
                ),
            ),
            (
                "Financial Abundance",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Financial Abundance", "Financial Abundance"
                ),
            ),
            (
                "Guidance and Protection",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Guidance and Protection", "Guidance and Protection"
                ),
            ),
            (
                "Special Intentions",
                PRAYER_CATEGORY_DISPLAY.get("Special Intentions", "Special Intentions"),
            ),
            ("Souls", PRAYER_CATEGORY_DISPLAY.get("Souls", "Souls")),
        ]


# ============================================
# FUNCTION-BASED VIEW (ALTERNATIVE)
# ============================================


def prayer_requests_view(request):
    """
    Function-based view alternative for prayer requests.
    Use this if you prefer function-based views over class-based views.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Rendered template with prayer requests context
    """
    # Require login
    if not request.user.is_authenticated:
        from django.shortcuts import redirect

        return redirect("login")

    # Get current month, week, and year
    today = date.today()
    current_month = today.strftime("%B")
    current_week = PrayerRequestsView._get_current_week(today)
    current_year = today.year

    # Get active prayer requests
    active_prayers = PrayerRequest.objects.filter(
        month=current_month, week=current_week, year=current_year, is_active=True
    ).order_by("category", "-created_at")

    # Group by category
    prayers_by_category = defaultdict(list)
    for prayer in active_prayers:
        prayers_by_category[prayer.category].append(prayer)

    context = {
        "current_month": current_month,
        "current_week": current_week,
        "current_year": current_year,
        "prayer_categories": [
            (
                "Thanksgiving",
                PRAYER_CATEGORY_DISPLAY.get("Thanksgiving", "Thanksgiving"),
            ),
            (
                "Healing and Good Health",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Healing and Good Health", "Healing and Good Health"
                ),
            ),
            ("Souls", PRAYER_CATEGORY_DISPLAY.get("Souls", "Souls")),
            (
                "Safety and Protection",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Safety and Protection", "Safety and Protection"
                ),
            ),
            (
                "Financial Abundance",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Financial Abundance", "Financial Abundance"
                ),
            ),
            (
                "Guidance and Protection",
                PRAYER_CATEGORY_DISPLAY.get(
                    "Guidance and Protection", "Guidance and Protection"
                ),
            ),
            (
                "Special Intentions",
                PRAYER_CATEGORY_DISPLAY.get("Special Intentions", "Special Intentions"),
            ),
        ],
        "prayer_requests": active_prayers,
        "prayer_requests_by_category": dict(prayers_by_category),
        "has_prayers": bool(active_prayers),
    }

    return render(request, "ministryhub/prayer_requests.html", context)


# ============================================
# UTILITY FUNCTION
# ============================================


def get_prayer_statistics(year=None):
    """
    Get prayer request statistics.
    Useful for dashboard or analytics pages.

    Args:
        year: Optional year filter. Defaults to current year.

    Returns:
        dict: Statistics about prayer requests
    """
    if year is None:
        year = date.today().year

    all_prayers = PrayerRequest.objects.filter(year=year)
    active_prayers = all_prayers.filter(is_active=True)

    stats = {
        "total_prayers": all_prayers.count(),
        "active_prayers": active_prayers.count(),
        "inactive_prayers": all_prayers.filter(is_active=False).count(),
        "by_category": {},
        "by_month": {},
    }

    # Count by category
    for prayer in all_prayers:
        category = prayer.category
        if category not in stats["by_category"]:
            stats["by_category"][category] = {
                "total": 0,
                "active": 0,
            }
        stats["by_category"][category]["total"] += 1
        if prayer.is_active:
            stats["by_category"][category]["active"] += 1

    # Count by month
    for month in [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]:
        month_prayers = all_prayers.filter(month=month)
        stats["by_month"][month] = {
            "total": month_prayers.count(),
            "active": month_prayers.filter(is_active=True).count(),
        }

    return stats
