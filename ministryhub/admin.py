from django import forms
from django.contrib import admin

from ministryhub.models import MINISTRY_CHOICES

from .models import BibleVerse, Event, Profile


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

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the ministry field with existing values
        if self.instance.ministry:
            self.fields["ministry"].initial = self.instance.ministry

    def clean(self):
        cleaned_data = super().clean()
        # The model's clean() will be called during full_clean()
        return cleaned_data

    def save(self, commit=True):
        # Convert the list of selected ministries back to the JSONField format
        instance = super().save(commit=False)
        instance.ministry = self.cleaned_data.get("ministry", [])
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
        "birthday",
        "spouse",
        "get_ministry_display_list",
    )
    search_fields = ("user__username", "first_name", "last_name")
    list_filter = ("birthday",)
    autocomplete_fields = ("user", "spouse")
    readonly_fields = ("id",)
    fieldsets = (
        ("User Information", {"fields": ("id", "user", "spouse")}),
        ("Personal Details", {"fields": ("first_name", "last_name", "birthday")}),
        ("Contact & Social", {"fields": ("facebook_page",)}),
        (
            "Ministry Assignment",
            {"fields": ("ministry",), "description": "Select all relevant ministries"},
        ),
    )

    def get_ministry_display_list(self, obj):
        """Display ministries as a readable comma-separated list in the admin list view"""
        if not obj.ministry:
            return "—"
        return ", ".join(obj.ministry)

    get_ministry_display_list.short_description = "Ministries"
