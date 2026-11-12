from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .forms import FarmerProfileForm

User = get_user_model()


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        role = request.POST.get("role", "")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check password confirmation
        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match."
            })

        # Check selected account type
        if role not in ["CUSTOMER", "FARMER"]:
            return render(request, "register.html", {
                "error": "Please select a valid account type."
            })

        # Check existing username and email
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "This username is already taken."
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, "register.html", {
                "error": "This email is already registered."
            })
        if User.objects.filter(phone=phone).exists():
            return render(request, "register.html", {
                "error": "This phone number is already registered."
            })

        # Create account securely
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            role=role
        )

        return render(request, "register.html", {
            "success": "Your account has been created successfully!"
        })

    return render(request, "register.html")

def user_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        # Find account using registered phone number
        users = User.objects.filter(phone=phone)

        if users.count() != 1:
            return render(request, "login.html", {
                "error": "Invalid phone number or password."
            })

        user = users.first()

        # Verify password securely using Django
        authenticated_user = authenticate(
            request,
            username=user.username,
            password=password
        )

        if authenticated_user is not None:
            if not authenticated_user.is_active:
                return render(request, "login.html", {
                    "error": "Your account is inactive."
                })

            login(request, authenticated_user)

            # Temporary redirect until dashboards are built
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid phone number or password."
        })

    return render(request, "login.html")
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_redirect(request):
    if request.user.role == "FARMER":
        return redirect("farmer_dashboard")

    elif request.user.role == "CUSTOMER":
        return redirect("customer_dashboard")

    return redirect("login")


@login_required
def customer_dashboard(request):
    if request.user.role != "CUSTOMER":
        return redirect("dashboard")

    return render(request, "customer_dashboard.html")


@login_required
def farmer_dashboard(request):
    if request.user.role != "FARMER":
        return redirect("dashboard")

    from marketplace.models import Crop, OrderItem
    from django.db.models import Sum

    crops = Crop.objects.filter(farmer=request.user)

    total_crops = crops.count()

    # Keep kg and grams separate; they cannot be added together.
    available_stock_kg = crops.filter(
        is_available=True,
        unit="KG"
    ).aggregate(total=Sum("quantity"))["total"] or 0

    available_stock_g = crops.filter(
        is_available=True,
        unit="G"
    ).aggregate(total=Sum("quantity"))["total"] or 0

    # Order items waiting for farmer action.
    new_orders = OrderItem.objects.filter(
        farmer=request.user,
        status="PENDING"
    ).count()

    # Sales value from completed order items.
    completed_sales = OrderItem.objects.filter(
        farmer=request.user,
        status="COMPLETED"
    ).aggregate(total=Sum("total_price"))["total"] or 0

    context = {
        "total_crops": total_crops,
        "available_stock_kg": available_stock_kg,
        "available_stock_g": available_stock_g,
        "new_orders": new_orders,
        "completed_sales": completed_sales,
    }

    return render(request, "farmer_dashboard.html", context)

@login_required
def farmer_location(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can update farm location.")
        return redirect("dashboard")

    if request.method == "POST":
        village = request.POST.get("village", "").strip()
        mandal = request.POST.get("mandal", "").strip()
        district = request.POST.get("district", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        latitude = request.POST.get("latitude", "").strip()
        longitude = request.POST.get("longitude", "").strip()

        if not all([village, mandal, district, pincode]):
            messages.error(request, "Please complete all address fields.")

        elif not pincode.isdigit() or len(pincode) != 6:
            messages.error(request, "Enter a valid 6-digit pincode.")

        else:
            from decimal import Decimal, InvalidOperation

            try:
                lat = Decimal(latitude) if latitude else None
                lon = Decimal(longitude) if longitude else None

                if (lat is None) != (lon is None):
                    raise ValueError("Both GPS coordinates are required.")

                if lat is not None and (
                    not lat.is_finite()
                    or not lon.is_finite()
                    or not -90 <= lat <= 90
                    or not -180 <= lon <= 180
                ):
                    raise ValueError("Invalid GPS coordinates.")

            except (InvalidOperation, ValueError):
                messages.error(request, "Invalid GPS location. Please capture it again.")
                return render(request, "location_setup.html")

            user = request.user
            user.village = village
            user.mandal = mandal
            user.district = district
            user.pincode = pincode
            user.latitude = lat
            user.longitude = lon
            user.save()

            messages.success(request, "Your farm location was saved successfully!")
            return redirect("farmer_dashboard")

    return render(request, "location_setup.html")
@login_required
def customer_location(request):
    if request.user.role != "CUSTOMER":
        messages.error(request, "Only customers can update their location.")
        return redirect("dashboard")

    if request.method == "POST":
        village = request.POST.get("village", "").strip()
        mandal = request.POST.get("mandal", "").strip()
        district = request.POST.get("district", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        latitude = request.POST.get("latitude", "").strip()
        longitude = request.POST.get("longitude", "").strip()

        if not all([village, mandal, district, pincode]):
            messages.error(request, "Please complete all address fields.")

        elif not pincode.isdigit() or len(pincode) != 6:
            messages.error(request, "Enter a valid 6-digit pincode.")

        else:
            from decimal import Decimal, InvalidOperation

            try:
                lat = Decimal(latitude) if latitude else None
                lon = Decimal(longitude) if longitude else None

                if (lat is None) != (lon is None):
                    raise ValueError()

                if lat is not None and (
                    not lat.is_finite()
                    or not lon.is_finite()
                    or not -90 <= lat <= 90
                    or not -180 <= lon <= 180
                ):
                    raise ValueError()

            except (InvalidOperation, ValueError):
                messages.error(request, "Invalid GPS location. Please capture it again.")
                return render(request, "customer_location.html")

            user = request.user
            user.village = village
            user.mandal = mandal
            user.district = district
            user.pincode = pincode
            user.latitude = lat
            user.longitude = lon
            user.save()

            messages.success(request, "Your location was saved successfully!")
            return redirect("customer_dashboard")

    return render(request, "customer_location.html")
@login_required
def farmer_profile(request):
    if request.user.role != "FARMER":
        messages.error(request, "Only farmers can access this profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = FarmerProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Your farm profile was updated successfully!")
            return redirect("farmer_profile")
    else:
        form = FarmerProfileForm(instance=request.user)

    return render(request, "farmer_profile.html", {
        "form": form,
        "farmer": request.user,
    })


def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")