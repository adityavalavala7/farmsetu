from django import forms
from .models import User


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "farm_name",
            "farm_description",
            "profile_photo",
        ]

        widgets = {
            "farm_name": forms.TextInput(attrs={
                "placeholder": "Enter your farm name",
                "class": "form-control",
            }),

            "farm_description": forms.Textarea(attrs={
                "placeholder": "Tell customers about your farm...",
                "rows": 5,
                "class": "form-control",
            }),

            "profile_photo": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "class": "form-control",
            }),
        }