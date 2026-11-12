
from decimal import Decimal

from django.db import models
from django.conf import settings


class Crop(models.Model):

    CATEGORY_CHOICES = [
        ("VEGETABLES", "Vegetables"),
        ("FRUITS", "Fruits"),
        ("GRAINS", "Grains"),
        ("PULSES", "Pulses"),
        ("LEAFY_GREENS", "Leafy Greens"),
    ]

    UNIT_CHOICES = [
        ("KG", "Kilograms (kg)"),
        ("G", "Grams (g)"),
    ]

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crops"
    )

    name = models.CharField(max_length=150)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=2,
        choices=UNIT_CHOICES,
        default="KG"
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    image = models.ImageField(
        upload_to="crops/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.farmer.username}"

    class Meta:
        ordering = ["-created_at"]


class CartItem(models.Model):

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "crop"],
                name="unique_customer_crop_cart"
            )
        ]

    def __str__(self):
        return f"{self.customer.username} - {self.crop.name}"


class Order(models.Model):

    PAYMENT_CHOICES = [
        ("CASH", "Cash on Delivery / Pickup"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    DELIVERY_CHOICES = [
        ("DELIVERY", "Home Delivery"),
        ("PICKUP", "Farmer Pickup"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PREPARING", "Preparing"),
        ("READY", "Ready for Pickup"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_CHOICES
    )

    delivery_address = models.TextField(blank=True)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"


class OrderItem(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_order_items"
    )

    crop_name = models.CharField(max_length=150)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    unit = models.CharField(
        max_length=2,
        choices=Crop.UNIT_CHOICES
    )

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("CONFIRMED", "Confirmed"),
            ("PREPARING", "Preparing"),
            ("READY", "Ready for Pickup"),
            ("OUT_FOR_DELIVERY", "Out for Delivery"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="PENDING",
    )

    # Individual farmer's cash collection status
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    # FarmSetu commission
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("4.50")
    )

    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    def __str__(self):
        return f"{self.crop_name} - Order #{self.order.id}"

from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="review"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="given_reviews"
    )

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_reviews"
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name="reviews"
    )

    farmer_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    crop_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.customer.username} for {self.crop.name}"
