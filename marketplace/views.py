from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Crop, CartItem
from decimal import Decimal, InvalidOperation
from .forms import CropForm
import math
from django.db import transaction
from .models import CartItem, Crop, Order, OrderItem
from django.db.models import Sum
from .forms import ReviewForm
from .models import Review



def home(request):
    return render(request, "home.html")


@login_required
def add_crop(request):

    # Only farmers can add crops
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can add crops.")
        return redirect("dashboard")

    if request.method == "POST":

        form = CropForm(request.POST, request.FILES)

        if form.is_valid():

            crop = form.save(commit=False)

            # Automatically assign the logged-in farmer
            crop.farmer = request.user

            crop.save()

            messages.success(
                request,
                "Your crop has been added successfully!"
            )

            return redirect("farmer_dashboard")

    else:
        form = CropForm()

    return render(request, "add_crop.html", {"form": form})
@login_required
def my_listings(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can view their listings.")
        return redirect("dashboard")

    crops = Crop.objects.filter(farmer=request.user)

    return render(request, "my_listings.html", {
        "crops": crops
    })
@login_required
def edit_crop(request, crop_id):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can edit crops.")
        return redirect("dashboard")

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        farmer=request.user
    )

    if request.method == "POST":
        form = CropForm(request.POST, request.FILES, instance=crop)

        if form.is_valid():
            form.save()
            messages.success(request, "Crop updated successfully!")
            return redirect("my_listings")
    else:
        form = CropForm(instance=crop)

    return render(request, "edit_crop.html", {
        "form": form,
        "crop": crop
    })
@login_required
def delete_crop(request, crop_id):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can delete crops.")
        return redirect("dashboard")

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        farmer=request.user
    )

    if request.method == "POST":
        crop.delete()
        messages.success(request, "Crop deleted successfully!")
        return redirect("my_listings")

    return redirect("my_listings")

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates in kilometres.
    """
    earth_radius = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


@login_required
def explore_crops(request):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can explore crops.")
        return redirect("dashboard")

    customer = request.user

    # Check whether customer has saved GPS coordinates.
    if customer.latitude is None or customer.longitude is None:
        return render(request, "explore_crops.html", {
            "has_location": False,
        })

    # Get search radius.
    try:
        radius = float(request.GET.get("radius", 10))
        if radius not in [5, 10, 15, 20, 30]:
            radius = 10
    except (TypeError, ValueError):
        radius = 10

    search_query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    # Get available crops from farmers with GPS coordinates.
    crops = Crop.objects.filter(
        is_available=True,
        farmer__role="FARMER",
        farmer__latitude__isnull=False,
        farmer__longitude__isnull=False,
    ).select_related("farmer")

    if search_query:
        crops = crops.filter(name__icontains=search_query)

    if category:
        crops = crops.filter(category=category)

    nearby_crops = []

    for crop in crops:
        distance = calculate_distance(
            customer.latitude,
            customer.longitude,
            crop.farmer.latitude,
            crop.farmer.longitude,
        )

        if distance <= radius:
            nearby_crops.append({
                "crop": crop,
                "distance": round(distance, 2),
            })

    # Nearest farmer's crops appear first.
    nearby_crops.sort(key=lambda item: item["distance"])

    context = {
        "has_location": True,
        "nearby_crops": nearby_crops,
        "radius": radius,
        "search_query": search_query,
        "selected_category": category,
        "categories": Crop.CATEGORY_CHOICES,
        "result_count": len(nearby_crops),
    }

    return render(request, "explore_crops.html", context)

@login_required
def add_to_cart(request, crop_id):
    if request.method != "POST":
        return redirect("explore_crops")

    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can add crops to the cart.")
        return redirect("dashboard")

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        is_available=True,
        farmer__role="FARMER"
    )

    try:
        quantity = Decimal(request.POST.get("quantity", "1"))
    except (InvalidOperation, TypeError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("explore_crops")

    if quantity <= 0:
        messages.error(request, "Quantity must be greater than zero.")
        return redirect("explore_crops")

    if quantity > crop.quantity:
        messages.error(request, "Requested quantity exceeds available stock.")
        return redirect("explore_crops")

    cart_item, created = CartItem.objects.get_or_create(
        customer=request.user,
        crop=crop,
        defaults={"quantity": quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > crop.quantity:
            messages.error(request, "Not enough stock available.")
            return redirect("explore_crops")

        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity"])

    messages.success(request, f"{crop.name} added to your cart!")
    return redirect("explore_crops")

@login_required
def view_cart(request):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can access the cart.")
        return redirect("dashboard")

    cart_items = CartItem.objects.filter(
        customer=request.user
    ).select_related("crop", "crop__farmer")

    cart_data = []
    grand_total = Decimal("0.00")

    for item in cart_items:
        if item.crop.unit == "G":
            # Price is per 100 grams
            item_total = (
                item.crop.price * item.quantity / Decimal("100")
            )
        else:
            # Price is per kilogram
            item_total = item.crop.price * item.quantity

        item_total = item_total.quantize(Decimal("0.01"))
        grand_total += item_total

        cart_data.append({
            "item": item,
            "item_total": item_total,
        })

    context = {
        "cart_items": cart_data,
        "grand_total": grand_total.quantize(Decimal("0.01")),
        "cart_count": len(cart_data),
    }

    return render(request, "cart.html", context)

@login_required
def remove_cart_item(request, item_id):
    if request.user.role != "CUSTOMER":
        return redirect("dashboard")

    if request.method == "POST":
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            customer=request.user
        )

        cart_item.delete()
        messages.success(request, "Item removed from your cart.")

    return redirect("view_cart")

@login_required
def update_cart_item(request, item_id):
    if request.user.role != "CUSTOMER":
        return redirect("dashboard")

    if request.method == "POST":
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            customer=request.user
        )

        try:
            quantity = Decimal(
                request.POST.get("quantity", "0")
            )

        except (InvalidOperation, TypeError):
            messages.error(request, "Please enter a valid quantity.")
            return redirect("view_cart")

        if not quantity.is_finite() or quantity <= 0:
            messages.error(
                request,
                "Quantity must be a valid positive number."
            )

        elif not cart_item.crop.is_available:
            messages.error(
                request,
                "This crop is currently unavailable."
            )

        elif quantity > cart_item.crop.quantity:
            messages.error(
                request,
                f"Only {cart_item.crop.quantity} units are available."
            )

        else:
            cart_item.quantity = quantity
            cart_item.save(update_fields=["quantity"])

            messages.success(
                request,
                "Cart quantity updated successfully!"
            )

    return redirect("view_cart")

@login_required
def checkout(request):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can checkout.")
        return redirect("dashboard")

    cart_items = CartItem.objects.filter(
        customer=request.user
    ).select_related("crop", "crop__farmer")

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("view_cart")

    # Calculate the cart summary
    cart_data = []
    grand_total = Decimal("0.00")

    for item in cart_items:
        crop = item.crop

        if not crop.is_available or item.quantity > crop.quantity:
            messages.error(
                request,
                f"{crop.name} is unavailable or has insufficient stock."
            )
            return redirect("view_cart")

        if (
            not item.quantity.is_finite()
            or item.quantity <= 0
            or item.quantity != item.quantity.to_integral_value()
        ):
            messages.error(
                request,
                "Your cart contains an invalid quantity. Please update it."
            )
            return redirect("view_cart")

        if crop.unit == "G":
            item_total = crop.price * item.quantity / Decimal("100")
        else:
            item_total = crop.price * item.quantity

        item_total = item_total.quantize(Decimal("0.01"))
        grand_total += item_total

        cart_data.append({
            "item": item,
            "item_total": item_total,
        })

    grand_total = grand_total.quantize(Decimal("0.01"))

    # Process Place Order submission
    if request.method == "POST":

        # FarmSetu currently accepts cash payments only.
        # Never trust a payment method submitted by the browser.
        payment_method = "CASH"

        delivery_method = request.POST.get("delivery_method")

        delivery_address = request.POST.get(
            "delivery_address", ""
        ).strip()

        if delivery_method not in ["DELIVERY", "PICKUP"]:
            messages.error(
                request,
                "Please select a valid delivery method."
            )
            return redirect("checkout")

        if delivery_method == "DELIVERY" and not delivery_address:
            messages.error(
                request,
                "Please enter your delivery address."
            )
            return redirect("checkout")

        try:
            with transaction.atomic():

                # Lock crop records while checking and updating stock
                locked_items = list(
                    CartItem.objects.filter(
                        customer=request.user
                    ).select_related("crop", "crop__farmer")
                )

                if not locked_items:
                    messages.error(request, "Your cart is empty.")
                    return redirect("view_cart")

                locked_crop_ids = [
                    item.crop_id for item in locked_items
                ]

                locked_crops = {
                    crop.id: crop
                    for crop in Crop.objects.select_for_update().filter(
                        id__in=locked_crop_ids
                    )
                }

                order_total = Decimal("0.00")
                order_lines = []

                # Validate stock and calculate final prices again
                for item in locked_items:
                    crop = locked_crops.get(item.crop_id)

                    if crop is None or not crop.is_available:
                        raise ValueError(
                            f"{item.crop.name} is no longer available."
                        )

                    quantity = item.quantity

                    if (
                        not quantity.is_finite()
                        or quantity <= 0
                        or quantity != quantity.to_integral_value()
                    ):
                        raise ValueError(
                            f"Invalid quantity for {crop.name}."
                        )

                    if quantity > crop.quantity:
                        raise ValueError(
                            f"Only {crop.quantity} units of "
                            f"{crop.name} are available."
                        )

                    if crop.unit == "G":
                        item_total = (
                            crop.price * quantity / Decimal("100")
                        )
                    else:
                        item_total = crop.price * quantity

                    item_total = item_total.quantize(Decimal("0.01"))
                    order_total += item_total

                    order_lines.append({
                        "crop": crop,
                        "quantity": quantity,
                        "item_total": item_total,
                    })

                order_total = order_total.quantize(Decimal("0.01"))

                # Create the order with cash payment
                order = Order.objects.create(
                    customer=request.user,
                    payment_method="CASH",
                    payment_status="PENDING",
                    delivery_method=delivery_method,
                    delivery_address=(
                        delivery_address
                        if delivery_method == "DELIVERY"
                        else ""
                    ),
                    total_amount=order_total,
                    status="PENDING",
                )

                # Create order items and reduce stock
                for line in order_lines:
                    crop = line["crop"]
                    quantity = line["quantity"]

                    OrderItem.objects.create(
                        order=order,
                        crop=crop,
                        farmer=crop.farmer,
                        crop_name=crop.name,
                        quantity=quantity,
                        unit=crop.unit,
                        price_per_unit=crop.price,
                        total_price=line["item_total"],
                    )

                    crop.quantity -= quantity

                    if crop.quantity <= 0:
                        crop.is_available = False

                    crop.save(update_fields=[
                        "quantity",
                        "is_available",
                        "updated_at",
                    ])

                # Clear the cart after successful order creation
                CartItem.objects.filter(
                    customer=request.user
                ).delete()

        except ValueError as error:
            messages.error(request, str(error))
            return redirect("view_cart")

        return render(
            request,
            "order_success.html",
            {"order": order}
        )

    context = {
        "cart_data": cart_data,
        "grand_total": grand_total,
        "customer": request.user,
        "checkout_details": request.session.get(
            "checkout_details", {}
        ),
    }

    return render(request, "checkout.html", context)

@login_required
def my_orders(request):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can view their orders.")
        return redirect("dashboard")

    orders = (
        Order.objects.filter(customer=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "my_orders.html",
        {"orders": orders}
    )
@login_required
def farmer_orders(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can view incoming orders.")
        return redirect("dashboard")

    order_items = (
        OrderItem.objects.filter(farmer=request.user)
        .select_related("order", "order__customer", "crop")
        .order_by("-order__created_at")
    )

    return render(
        request,
        "farmer_orders.html",
        {"order_items": order_items}
    )
@login_required
def update_farmer_order_item(request, item_id):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can update orders.")
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("farmer_orders")

    try:
        with transaction.atomic():

            order_item = get_object_or_404(
                OrderItem.objects.select_for_update(),
                id=item_id,
                farmer=request.user,
            )

            order = order_item.order

            current_status = order_item.status
            new_status = request.POST.get("status")

            # Allowed status transitions
            allowed_transitions = {
                "PENDING": ["CONFIRMED", "CANCELLED"],
                "CONFIRMED": ["PREPARING", "CANCELLED"],
                "PREPARING": (
                    ["READY", "CANCELLED"]
                    if order.delivery_method == "PICKUP"
                    else ["OUT_FOR_DELIVERY", "CANCELLED"]
                ),
                "READY": ["COMPLETED"],
                "OUT_FOR_DELIVERY": ["COMPLETED"],
                "COMPLETED": [],
                "CANCELLED": [],
            }

            if new_status not in allowed_transitions.get(
                current_status, []
            ):
                messages.error(
                    request,
                    "This order status change is not allowed."
                )
                return redirect("farmer_orders")

            # Restore stock if farmer rejects/cancels the item
            if new_status == "CANCELLED":

                crop = Crop.objects.select_for_update().get(
                    id=order_item.crop_id
                )

                crop.quantity += order_item.quantity
                crop.is_available = True

                crop.save(update_fields=[
                    "quantity",
                    "is_available",
                    "updated_at",
                ])
            order_item.status = new_status

            update_fields = ["status"]

            if new_status == "COMPLETED":
                order_item.commission_amount = (
                    order_item.total_price * order_item.commission_rate / Decimal("100")
                ).quantize(Decimal("0.01"))

                update_fields.append("commission_amount")

            order_item.save(update_fields=update_fields)

            # Update the overall customer order status
            all_items = list(
                OrderItem.objects.filter(order=order)
            )

            active_items = [
                item for item in all_items
                if item.status != "CANCELLED"
            ]

            if not active_items:
                order.status = "CANCELLED"

            elif all(item.status == "COMPLETED" for item in active_items):
                order.status = "COMPLETED"

            else:
                # Overall order reflects the least advanced active item
                progress = {
                    "PENDING": 0,
                    "CONFIRMED": 1,
                    "PREPARING": 2,
                    "READY": 3,
                    "OUT_FOR_DELIVERY": 3,
                    "COMPLETED": 4,
                }

                least_advanced = min(
                    active_items,
                    key=lambda item: progress.get(item.status, 0)
                )

                order.status = least_advanced.status

                if order.status == "READY":
                    order.status = "READY"
                elif order.status == "OUT_FOR_DELIVERY":
                    order.status = "OUT_FOR_DELIVERY"

            order.save(update_fields=["status", "updated_at"])

        messages.success(
            request,
            f"{order_item.crop_name} order updated successfully."
        )

    except Crop.DoesNotExist:
        messages.error(request, "The crop associated with this order was not found.")

    return redirect("farmer_orders")

@login_required
def confirm_cash_received(request, item_id):

    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can confirm cash payments.")
        return redirect("dashboard")

    if request.method != "POST":
        return redirect("farmer_orders")

    try:
        with transaction.atomic():

            order_item = get_object_or_404(
                OrderItem.objects.select_for_update(),
                id=item_id,
                farmer=request.user
            )

            order = Order.objects.select_for_update().get(
                id=order_item.order_id
            )

            # Do not apply cash confirmation to historical online orders.
            if order.payment_method != "CASH":
                messages.error(
                    request,
                    "This order was not placed using cash payment."
                )
                return redirect("farmer_orders")

            if order_item.status != "COMPLETED":
                messages.error(
                    request,
                    "You can confirm cash only after completing the order."
                )
                return redirect("farmer_orders")

            if order_item.payment_status == "PAID":
                messages.info(
                    request,
                    "Cash has already been confirmed for this item."
                )
                return redirect("farmer_orders")

            # Confirm payment for this farmer's item only.
            order_item.payment_status = "PAID"
            order_item.save(update_fields=["payment_status"])

            # Update the overall order payment status only when
            # every non-cancelled item has been paid.
            active_items = OrderItem.objects.filter(
                order=order
            ).exclude(status="CANCELLED")

            if active_items.exists() and not active_items.exclude(
                payment_status="PAID"
            ).exists():
                order.payment_status = "PAID"
            else:
                order.payment_status = "PENDING"

            order.save(update_fields=[
                "payment_status",
                "updated_at"
            ])

        messages.success(
            request,
            f"Cash received successfully for {order_item.crop_name}!"
        )

    except Order.DoesNotExist:
        messages.error(request, "Order not found.")

    return redirect("farmer_orders")

@login_required
def manage_inventory(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can manage inventory.")
        return redirect("dashboard")

    if request.method == "POST":
        crop_id = request.POST.get("crop_id")
        action = request.POST.get("action")

        crop = get_object_or_404(
            Crop,
            id=crop_id,
            farmer=request.user
        )

        if action == "update_stock":
            try:
                quantity = Decimal(request.POST.get("quantity", ""))

                if not quantity.is_finite() or quantity < 0:
                    raise ValueError

                if quantity != quantity.to_integral_value():
                    raise ValueError

                crop.quantity = quantity

                if quantity == 0:
                    crop.is_available = False

                crop.save()
                messages.success(
                    request,
                    f"{crop.name} stock updated successfully."
                )

            except (InvalidOperation, ValueError):
                messages.error(
                    request,
                    "Enter a valid whole-number stock quantity."
                )

        elif action == "toggle_availability":
            if crop.quantity <= 0 and not crop.is_available:
                messages.error(
                    request,
                    "Add stock before making this crop available."
                )
            else:
                crop.is_available = not crop.is_available
                crop.save()
                messages.success(
                    request,
                    f"{crop.name} availability updated."
                )

        return redirect("manage_inventory")

    crops = Crop.objects.filter(
        farmer=request.user
    ).order_by("name")

    return render(
        request,
        "manage_inventory.html",
        {"crops": crops}
    )
@login_required
def farmer_earnings(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can view earnings.")
        return redirect("dashboard")

    # Get completed order items belonging to this farmer
    completed_items = OrderItem.objects.filter(
        farmer=request.user,
        status="COMPLETED"
    ).select_related("order").order_by("-order__created_at")

    # Total completed sales
    total_sales = completed_items.aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")

    # Total FarmSetu commission
    total_commission = completed_items.aggregate(
        total=Sum("commission_amount")
    )["total"] or Decimal("0.00")

    # Farmer's net earnings
    net_earnings = total_sales - total_commission

    # Cash actually confirmed as received
    cash_collected = completed_items.filter(
        payment_status="PAID"
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")

    # Completed orders with cash still pending
    cash_pending = completed_items.filter(
        payment_status="PENDING"
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")
    for item in completed_items:
        item.net_amount = item.total_price - item.commission_amount

    context = {
        "completed_items": completed_items,
        "total_sales": total_sales,
        "total_commission": total_commission,
        "net_earnings": net_earnings,
        "cash_collected": cash_collected,
        "cash_pending": cash_pending,
    }

    return render(request, "farmer_earnings.html", context)
@login_required
def track_order(request, order_id):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can track orders.")
        return redirect("dashboard")

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "items__farmer"
        ),
        id=order_id,
        customer=request.user
    )

    return render(request, "track_order.html", {
        "order": order,
        "items": order.items.all(),
    })


@login_required
def submit_review(request, item_id):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can submit reviews.")
        return redirect("dashboard")

    order_item = get_object_or_404(
        OrderItem.objects.select_related("order", "farmer", "crop"),
        id=item_id,
        order__customer=request.user
    )

    if order_item.status != "COMPLETED":
        messages.error(
            request,
            "You can review an item only after it is completed."
        )
        return redirect("my_orders")

    if Review.objects.filter(order_item=order_item).exists():
        messages.info(request, "You have already reviewed this item.")
        return redirect("my_orders")

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.order_item = order_item
            review.customer = request.user
            review.farmer = order_item.farmer
            review.crop = order_item.crop
            review.save()

            messages.success(request, "Your review was submitted successfully!")
            return redirect("my_orders")
    else:
        form = ReviewForm()

    return render(request, "submit_review.html", {
        "form": form,
        "order_item": order_item,
    })
