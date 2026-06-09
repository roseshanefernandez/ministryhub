from django import forms
from django.core.validators import URLValidator

from .models import GENDER_CHOICES, MINISTRY_CHOICES, Profile


class ProfileForm(forms.ModelForm):
    # Use a MultipleChoiceField mapped to the JSON list on the model
    ministry = forms.MultipleChoiceField(
        choices=MINISTRY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect,
    )
    priority_ministry = forms.ChoiceField(
        choices=MINISTRY_CHOICES,
        required=True,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "birthday",
            "gender",
            "spouse",
            "facebook_page",
            "ministry",
            "priority_ministry",
        ]

        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        # Filter spouse queryset to show only opposite gender profiles
        if request_user is not None and hasattr(request_user, "profile"):
            user_profile = request_user.profile
            opposite_gender = "F" if user_profile.gender == "M" else "M"
            self.fields["spouse"].queryset = Profile.objects.filter(
                gender=opposite_gender
            ).exclude(id=user_profile.id)
        else:
            # If no profile yet, show all profiles but exclude current user
            if request_user is not None:
                self.fields["spouse"].queryset = self.fields["spouse"].queryset.exclude(
                    user=request_user
                )

        self.fields["spouse"].required = False
