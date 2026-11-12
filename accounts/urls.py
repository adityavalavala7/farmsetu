
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("farmer/dashboard/", views.farmer_dashboard, name="farmer_dashboard"),
    path("farmer/location/", views.farmer_location, name="farmer_location"),
    path("customer/location/", views.customer_location, name="customer_location"),
    path("farmer/profile/", views.farmer_profile, name="farmer_profile"),
]

