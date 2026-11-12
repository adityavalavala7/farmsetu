# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('FARMER', 'Farmer'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )
        # Farmer location information
    village = models.CharField(max_length=100, blank=True)
    mandal = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # GPS coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    farm_name = models.CharField(
    max_length=150,
    blank=True
    )

    farm_description = models.TextField(
        blank=True
    )

    profile_photo = models.ImageField(
        upload_to="farmer_profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"