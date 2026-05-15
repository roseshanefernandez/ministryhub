from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Centralized ministry choices for reuse in forms and validation
MINISTRY_CHOICES = [
    ("AKM", "AKM"),
    ("Mercy", "Mercy"),
    ("Couples", "Couples"),
    ("Worship", "Worship"),
    ("Liturgy", "Liturgy"),
    ("Events", "Events"),
    ("Media", "Media"),
]
ALLOWED_MINISTRY_VALUES = {c[0] for c in MINISTRY_CHOICES}


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    birthday = models.DateField()
    spouse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spouses",
    )
    facebook_page = models.CharField(max_length=150, blank=True, null=True)
    # Optional multi-select ministry membership, stored as list of strings
    ministry = models.JSONField(blank=True, default=list)

    def clean(self):
        super().clean()
        # Prevent selecting self as spouse
        if self.spouse and self.user_id and self.spouse_id == self.user_id:
            raise ValidationError({"spouse": "You cannot select yourself as a spouse."})
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

    def __str__(self):
        return f"Profile({self.user.username})"


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
