from django import forms
from django.contrib import admin

from ministryhub.models import MINISTRY_CHOICES

from .models import Announcement, BibleVerse, Event, Profile


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "active")
    list_filter = ("active",)

    class Meta:
        model = Announcement
        fields = "__all__"


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ("verse_id", "date")

    class Meta:
        model = BibleVerse
        fields = "__all__"


class EventAdminForm(forms.ModelForm):
    ministry = forms.MultipleChoiceField(
        choices=MINISTRY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the ministries involved in this event",
    )

    class Meta:
        model = Event
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the ministry field with existing values
        if self.instance.ministry:
            self.fields["ministry"].initial = self.instance.ministry

    def save(self, commit=True):
        # Convert the list of selected ministries back to the JSONField format
        instance = super().save(commit=False)
        instance.ministry = self.cleaned_data.get("ministry", [])
        if commit:
            instance.save()
        return instance


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ("name", "start_date", "end_date", "closed", "display_ministries")
    list_filter = ("closed", "ministry")
    search_fields = ("name", "caption")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "caption", "description")}),
        (
            "Event Details",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "location",
                    "registration_link",
                    "poster",
                    "closed",
                )
            },
        ),
        (
            "Ministry Assignment",
            {"fields": ("ministry",), "description": "Select all relevant ministries"},
        ),
    )

    def display_ministries(self, obj):
        """Display ministries as a readable list in the admin list view"""
        if obj.ministry:
            return ", ".join(obj.ministry)
        return "—"

    display_ministries.short_description = "Ministries"


class ProfileAdminForm(forms.ModelForm):
    ministry = forms.MultipleChoiceField(
        choices=MINISTRY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the ministries this person is involved with",
    )

    priority_ministry = forms.ChoiceField(
        choices=MINISTRY_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        help_text="Select the priority ministry this person is involved with",
    )

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the ministry field with existing values
        if self.instance.ministry:
            self.fields["ministry"].initial = self.instance.ministry
        if self.instance.priority_ministry:
            self.fields["priority_ministry"].initial = self.instance.priority_ministry

    def clean(self):
        cleaned_data = super().clean()
        # The model's clean() will be called during full_clean()
        return cleaned_data

    def save(self, commit=True):
        # Convert the list of selected ministries back to the JSONField format
        instance = super().save(commit=False)
        instance.ministry = self.cleaned_data.get("ministry", [])
        instance.priority_ministry = self.cleaned_data.get("priority_ministry")
        if commit:
            instance.save()
        return instance


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "gender",
        "birthday",
        "spouse",
        "get_ministry_display_list",
    )
    search_fields = ("user__username", "first_name", "last_name", "user__email")
    list_filter = ("gender", "birthday")
    autocomplete_fields = ("user", "spouse")
    readonly_fields = ("id",)
    fieldsets = (
        ("User Information", {"fields": ("id", "user")}),
        (
            "Personal Details",
            {"fields": ("first_name", "last_name", "gender", "birthday")},
        ),
        ("Spouse", {"fields": ("spouse",)}),
        ("Contact & Social", {"fields": ("facebook_page",)}),
        (
            "Ministry Assignment",
            {
                "fields": ("ministry", "priority_ministry"),
                "description": "Select all relevant ministries",
            },
        ),
    )

    def get_ministry_display_list(self, obj):
        """Display ministries as a readable comma-separated list in the admin list view"""
        if not obj.ministry:
            return "—"
        return ", ".join(obj.ministry)

    get_ministry_display_list.short_description = "Ministries"


"""
Django Admin Configuration for Prayer Requests
Includes custom filters, bulk actions, and enhanced admin interface
"""

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.html import format_html

from .models import PrayerRequest


class MonthFilter(admin.SimpleListFilter):
    """Custom filter for prayer request months"""

    title = "Month"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        months = [
            ("January", "January"),
            ("February", "February"),
            ("March", "March"),
            ("April", "April"),
            ("May", "May"),
            ("June", "June"),
            ("July", "July"),
            ("August", "August"),
            ("September", "September"),
            ("October", "October"),
            ("November", "November"),
            ("December", "December"),
        ]
        return months

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(month=self.value())
        return queryset


class WeekFilter(admin.SimpleListFilter):
    """Custom filter for prayer request weeks"""

    title = "Week"
    parameter_name = "week"

    def lookups(self, request, model_admin):
        weeks = [
            (1, "Week 1"),
            (2, "Week 2"),
            (3, "Week 3"),
            (4, "Week 4"),
            (5, "Week 5"),
        ]
        return weeks

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(week=int(self.value()))
        return queryset


class ActiveStatusFilter(admin.SimpleListFilter):
    """Custom filter for active/inactive prayer requests"""

    title = "Active Status"
    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return [
            ("active", "Active"),
            ("inactive", "Inactive"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        return queryset


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Prayer Requests with:
    - Custom filters by month, week, and active status
    - Bulk actions to set/unset active status
    - Read-only fields and custom formatting
    - Optimized list display
    """

    list_display = (
        "category",
        "month",
        "week",
        "year",
        "active_status_indicator",
        "description_preview",
        "created_at_formatted",
    )

    list_filter = (
        MonthFilter,
        WeekFilter,
        ActiveStatusFilter,
        "category",
        "year",
        "created_at",
    )

    search_fields = (
        "category",
        "description",
        "month",
    )

    fieldsets = (
        ("Basic Information", {"fields": ("category", "description")}),
        (
            "Schedule",
            {
                "fields": ("month", "week", "year"),
                "description": "Specify when this prayer request should be displayed",
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
                "description": "Only active prayer requests will be displayed on the prayer page",
            },
        ),
        ("Meta", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at",)

    actions = [
        "make_active",
        "make_inactive",
        "activate_current_week",
        "deactivate_all",
    ]

    ordering = ("-year", "-created_at")

    # ============================================
    # CUSTOM DISPLAY METHODS
    # ============================================

    def active_status_indicator(self, obj):
        """Display active status with color indicator"""
        if obj.is_active:
            return format_html(
                '<span style="color: #228B22; font-weight: bold;">● Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #8B0000; font-weight: bold;">● Inactive</span>'
            )

    active_status_indicator.short_description = "Status"

    def description_preview(self, obj):
        """Display truncated description"""
        if len(obj.description) > 75:
            return obj.description[:75] + "..."
        return obj.description

    description_preview.short_description = "Description"

    def created_at_formatted(self, obj):
        """Display formatted creation date"""
        return obj.created_at.strftime("%b %d, %Y at %I:%M %p")

    created_at_formatted.short_description = "Created"

    # ============================================
    # BULK ACTIONS
    # ============================================

    def make_active(self, request, queryset: QuerySet):
        """Bulk action: Set selected prayer requests to active"""
        updated_count = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated_count} prayer request(s) marked as active."
        )

    make_active.short_description = "✓ Mark selected as Active"

    def make_inactive(self, request, queryset: QuerySet):
        """Bulk action: Set selected prayer requests to inactive"""
        updated_count = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated_count} prayer request(s) marked as inactive."
        )

    make_inactive.short_description = "✗ Mark selected as Inactive"

    def activate_current_week(self, request, queryset: QuerySet):
        """Bulk action: Activate current week's prayers"""
        from datetime import datetime

        current_month = datetime.now().strftime("%B")
        first_day = datetime.now().replace(day=1)
        current_week = (datetime.now().day + first_day.weekday()) // 7 + 1
        current_year = datetime.now().year

        updated_count = PrayerRequest.objects.filter(
            month=current_month, week=current_week, year=current_year
        ).update(is_active=True)

        # Also deactivate all other prayers
        PrayerRequest.objects.exclude(
            month=current_month, week=current_week, year=current_year
        ).update(is_active=False)

        self.message_user(
            request,
            f"Activated {updated_count} prayer request(s) for {current_month} Week {current_week}. "
            f"All other prayers have been deactivated.",
        )

    activate_current_week.short_description = "🔄 Activate Current Week Only"

    def deactivate_all(self, request, queryset: QuerySet):
        """Bulk action: Deactivate all prayer requests"""
        updated_count = PrayerRequest.objects.all().update(is_active=False)
        self.message_user(
            request, f"{updated_count} prayer request(s) have been deactivated."
        )

    deactivate_all.short_description = "⊘ Deactivate All"

    # ============================================
    # CUSTOMIZATION
    # ============================================

    class Media:
        css = {"all": ("admin/css/prayer_admin.css",)}

    def changelist_view(self, request, extra_context=None):
        """Add extra context to the changelist view"""
        extra_context = extra_context or {}
        extra_context["title"] = "Prayer Requests Management"
        return super().changelist_view(request, extra_context=extra_context)
