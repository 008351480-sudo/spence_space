from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Household


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    HOUSEHOLD_CHOICES = [
        ("create", "Create a new household"),
        ("join", "Join an existing household with an invite code"),
    ]
    household_action = forms.ChoiceField(
        choices=HOUSEHOLD_CHOICES,
        widget=forms.RadioSelect,
        initial="create",
        label="Family / Household",
    )
    household_name = forms.CharField(
        max_length=100,
        required=False,
        help_text="Only needed if you're creating a new household (e.g. 'The Smith Family').",
    )
    invite_code = forms.CharField(
        max_length=8,
        required=False,
        help_text="Only needed if you're joining an existing household.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("household_action")

        if action == "create" and not cleaned_data.get("household_name"):
            self.add_error("household_name", "Please name your household.")

        if action == "join":
            code = (cleaned_data.get("invite_code") or "").upper()
            if not code:
                self.add_error("invite_code", "Enter the invite code you were given.")
            elif not Household.objects.filter(invite_code=code).exists():
                self.add_error("invite_code", "That invite code doesn't match any household.")

        return cleaned_data
