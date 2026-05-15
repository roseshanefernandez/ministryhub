from django import forms
from django.core.validators import URLValidator

from .models import MINISTRY_CHOICES, Profile


class ProfileForm(forms.ModelForm):
    # Use a MultipleChoiceField mapped to the JSON list on the model
    ministry = forms.MultipleChoiceField(
        choices=MINISTRY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "birthday",
            "spouse",
            "facebook_page",
            "ministry",
        ]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)
        # Constrain spouse queryset to exclude the current user if available
        if request_user is not None and hasattr(self.fields.get("spouse"), "queryset"):
            self.fields["spouse"].queryset = self.fields["spouse"].queryset.exclude(
                pk=request_user.pk
            )
