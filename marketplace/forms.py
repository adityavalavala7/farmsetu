from django import forms
from .models import Crop


class CropForm(forms.ModelForm):

    class Meta:
        model = Crop

        fields = [
            "name",
            "category",
            "description",
            "price",
            "unit",
            "quantity",
            "image",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "e.g. Fresh Tomatoes",
                "class": "form-control",
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Describe your crop...",
                "rows": 4,
                "class": "form-control",
            }),

            "price": forms.NumberInput(attrs={
                "placeholder": "Enter price",
                "min": "0.01",
                "step": "0.01",
                "class": "form-control",
            }),

            "unit": forms.Select(attrs={
                "class": "form-control",
            }),

            "quantity": forms.NumberInput(attrs={
                "placeholder": "Available quantity",
                "min": "0.001",
                "step": "0.001",
                "class": "form-control",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")

        return price

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")

        return quantity
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["farmer_rating", "crop_rating", "comment"]

        widgets = {
            "farmer_rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Excellent"),
                    (4, "★★★★ - Very Good"),
                    (3, "★★★ - Good"),
                    (2, "★★ - Fair"),
                    (1, "★ - Poor"),
                ],
                attrs={"class": "form-control"}
            ),
            "crop_rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Excellent"),
                    (4, "★★★★ - Very Good"),
                    (3, "★★★ - Good"),
                    (2, "★★ - Fair"),
                    (1, "★ - Poor"),
                ],
                attrs={"class": "form-control"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share your experience..."
                }
            ),
        }