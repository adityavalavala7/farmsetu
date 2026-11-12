
from django.contrib import admin
from .models import Crop, CartItem, Order, OrderItem


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "farmer",
        "price",
        "unit",
        "quantity",
        "is_available",
        "created_at",
    )

    list_filter = (
        "category",
        "unit",
        "is_available",
    )

    search_fields = (
        "name",
        "farmer__username",
    )

    list_editable = (
        "price",
        "quantity",
        "is_available",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "crop",
        "quantity",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "crop__name",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "payment_method",
        "payment_status",
        "delivery_method",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "delivery_method",
    )

    search_fields = (
        "customer__username",
        "id",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "crop_name",
        "farmer",
        "quantity",
        "unit",
        "total_price",
    )

    search_fields = (
        "crop_name",
        "farmer__username",
    )
