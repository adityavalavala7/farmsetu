
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "phone",
        "role",
        "village",
        "district",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "district",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone",
        "village",
        "district",
        "pincode",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("FarmSetu Information", {
            "fields": (
                "role",
                "phone",
                "village",
                "mandal",
                "district",
                "pincode",
                "latitude",
                "longitude",
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("FarmSetu Information", {
            "fields": (
                "role",
                "phone",
            ),
        }),
    )

