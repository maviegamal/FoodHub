from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import JsonResponse

from core.api import ApiError, api, get_or_404, json_body
from menu.models import Food

from .models import STATUS_CANCELLED, STATUS_CHOICES, STATUS_FLOW, STATUS_PENDING, Order
from .views import order_dict

User = get_user_model()


@api(["GET"], auth="admin")
def admin_orders(request):
    qs = Order.objects.select_related("user").prefetch_related("items")
    return JsonResponse({"orders": [order_dict(o, admin=True) for o in qs]})


@api(["POST"], auth="admin")
def admin_order_status(request, order_id):
    order = get_or_404(Order.objects.select_related("user"), pk=order_id)
    status = json_body(request).get("status")
    if status not in dict(STATUS_CHOICES):
        raise ApiError("Unknown status.", 422)
    if status not in STATUS_FLOW[order.status]:
        raise ApiError(f"An order that is {order.get_status_display().lower()} cannot move to that status.", 409)
    order.status = status
    order.save(update_fields=["status"])
    order = Order.objects.select_related("user").prefetch_related("items").get(pk=order.pk)
    return JsonResponse({"order": order_dict(order, admin=True)})


@api(["GET"], auth="admin")
def admin_stats(request):
    revenue = (
        Order.objects.exclude(status=STATUS_CANCELLED).aggregate(total=Sum("total"))["total"]
        or Decimal("0")
    )
    return JsonResponse(
        {
            "users": User.objects.filter(is_superuser=False).count(),
            "suspended": User.objects.filter(is_superuser=False, is_active=False).count(),
            "foods": Food.objects.count(),
            "orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status=STATUS_PENDING).count(),
            "revenue": f"{revenue:.2f}",
        }
    )
