from django.urls import path
from . import views

urlpatterns = [
    path("add-crop/", views.add_crop, name="add_crop"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("edit-crop/<int:crop_id>/", views.edit_crop, name="edit_crop"),
    path("delete-crop/<int:crop_id>/", views.delete_crop, name="delete_crop"),
    path("explore/", views.explore_crops, name="explore_crops"),
    path("cart/add/<int:crop_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("farmer/orders/", views.farmer_orders, name="farmer_orders"),

    path(
        "farmer/orders/update/<int:item_id>/",
        views.update_farmer_order_item,
        name="update_farmer_order_item",
    ),
    path(
        "farmer/orders/confirm-cash/<int:item_id>/",
        views.confirm_cash_received,
        name="confirm_cash_received"
    ),
    path(
        "farmer/inventory/",
        views.manage_inventory,
        name="manage_inventory"
    ),
    path("farmer/earnings/", views.farmer_earnings, name="farmer_earnings"),
    path(
        "track-order/<int:order_id>/",
        views.track_order,
        name="track_order"
    ),
    path(
        "review/<int:item_id>/",
        views.submit_review,
        name="submit_review"
    ),
]