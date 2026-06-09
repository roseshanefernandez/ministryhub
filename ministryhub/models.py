from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Centralized ministry choices for reuse in forms and validation
MINISTRY_CHOICES = [
    ("AKM", "AKM"),
    ("Couples", "Couples"),
    ("Events", "Events"),
    ("Finance", "Finance"),
    ("Liturgy", "Liturgy"),
    ("Mercy", "Mercy"),
    ("Media", "Media"),
    ("Worship", "Worship"),
    ("No ministry yet", "No ministry yet"),
]
ALLOWED_MINISTRY_VALUES = {c[0] for c in MINISTRY_CHOICES}

# Gender choices for Profile
GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
]

# Prayer Request category choices
PRAYER_CATEGORY_CHOICES = [
    ("Thanksgiving", "Thanksgiving"),
    ("Healing and Good Health", "Healing and Good Health"),
    ("Souls", "Souls"),
    ("Financial Abundance", "Financial Abundance"),
    ("Guidance and Protection", "Guidance and Protection"),
    ("Special Intentions", "Special Intentions"),
]

# Month choices
MONTH_CHOICES = [
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

# Week choices
WEEK_CHOICES = [
    (1, "Week 1"),
    (2, "Week 2"),
    (3, "Week 3"),
    (4, "Week 4"),
    (5, "Week 5"),
]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    spouse = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="married_to",
    )
    facebook_page = models.CharField(max_length=150, blank=True, null=True)
    # Optional multi-select ministry membership, stored as list of strings
    ministry = models.JSONField(blank=True, default=list)
    priority_ministry = models.CharField(
        max_length=50, choices=MINISTRY_CHOICES, default="No ministry yet"
    )

    def clean(self):
        super().clean()
        # Prevent selecting self as spouse
        if self.spouse and self.spouse.id == self.id:
            raise ValidationError({"spouse": "You cannot select yourself as a spouse."})
        # Validate spouse has opposite gender
        if self.spouse and self.spouse.gender == self.gender:
            raise ValidationError({"spouse": "Spouse must be of opposite gender."})
        # Validate ministry values if provided
        if self.ministry is not None:
            if not isinstance(self.ministry, list):
                raise ValidationError(
                    {"ministry": "Invalid format. Expected a list of options."}
                )
            invalid = [m for m in self.ministry if m not in ALLOWED_MINISTRY_VALUES]
            if invalid:
                raise ValidationError(
                    {"ministry": f"Invalid selection(s): {', '.join(invalid)}."}
                )

    def save(self, *args, _skip_spouse_sync=False, **kwargs):
        current_spouse = None
        previous_spouse = None

        if self.pk:
            try:
                previous_spouse = Profile.objects.get(pk=self.pk).spouse
            except Profile.DoesNotExist:
                previous_spouse = None

        super().save(*args, **kwargs)

        if _skip_spouse_sync:
            return

        if previous_spouse and previous_spouse != self.spouse:
            # Clear previous spouse reference when spouse changes or is removed
            if previous_spouse.spouse_id == self.pk:
                previous_spouse.spouse = None
                previous_spouse.save(update_fields=["spouse"], _skip_spouse_sync=True)

        if self.spouse:
            current_spouse = self.spouse
            if current_spouse.spouse_id != self.pk:
                current_spouse.spouse = self
                current_spouse.save(update_fields=["spouse"], _skip_spouse_sync=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    caption = models.CharField(max_length=50)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    poster = models.ImageField(upload_to="events/")
    ministry = models.JSONField(blank=True, default=list)
    closed = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        super().clean()
        # Validate ministry values if provided
        if self.ministry is not None:
            if not isinstance(self.ministry, list):
                raise ValidationError(
                    {"ministry": "Invalid format. Expected a list of options."}
                )
            invalid = [m for m in self.ministry if m not in ALLOWED_MINISTRY_VALUES]
            if invalid:
                raise ValidationError(
                    {"ministry": f"Invalid selection(s): {', '.join(invalid)}."}
                )

    def save(self, *args, **kwargs):
        # Automatically set finished to True if event date is in the past
        if self.end_date < timezone.now().date():
            self.closed = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PrayerRequest(models.Model):
    category = models.CharField(
        max_length=50,
        choices=PRAYER_CATEGORY_CHOICES,
        default="Others",
    )
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    month = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES,
        default="January",
    )
    week = models.IntegerField(
        choices=WEEK_CHOICES,
        default=1,
    )
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-created_at"]

    def __str__(self):
        return f"{self.category} - {self.month} Week {self.week}, {self.year}"


class BibleVerse(models.Model):
    # Numeric boundaries for sorting and precise querying
    start_verse = models.IntegerField(db_index=True)
    end_verse = models.IntegerField(db_index=True, null=True)

    verse_text = models.TextField()
    book_name = models.CharField(max_length=100)
    chapter_number = models.IntegerField()
    verse_id = models.CharField(max_length=100)

    date = models.DateField(unique=True)

    class Meta:
        ordering = ["book_name", "chapter_number", "start_verse", "end_verse"]

    def save(self, *args, **kwargs):
        # Automatically fall back if end_verse is omitted
        if self.start_verse and not self.end_verse:
            self.end_verse = self.start_verse
        super().save(*args, **kwargs)

    def __str__(self):
        return self.verse_id


class Announcement(models.Model):
    title = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)