from django.urls import path

from . import admin_views, views

urlpatterns = [
    path("cart/", views.cart),
    path("cart/items/<int:food_id>/", views.cart_item),
    path("orders/", views.orders),
    path("orders/<int:order_id>/cancel/", views.cancel_order),
    path("admin/orders/", admin_views.admin_orders),
    path("admin/orders/<int:order_id>/status/", admin_views.admin_order_status),
    path("admin/stats/", admin_views.admin_stats),
]
