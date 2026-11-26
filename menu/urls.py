from django.urls import path

from . import views

urlpatterns = [
    path("foods/", views.food_list),
    path("admin/foods/", views.admin_foods),
    path("admin/foods/<int:food_id>/", views.admin_food_detail),
]
