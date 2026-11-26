import re
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse

from core.api import ApiError, api, get_or_404, json_body, to_int
from menu.models import Food

from .models import (
    MAX_QUANTITY,
    STATUS_CANCELLED,
    STATUS_FLOW,
    STATUS_PENDING,
    CartItem,
    Order,
    OrderItem,
)

PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def cart_dict(user):
    items = CartItem.objects.filter(user=user).select_related("food").order_by("id")
    rows, total, count = [], Decimal("0"), 0
    for item in items:
        food = item.food
        line = food.price * item.quantity
        if food.is_available:
            total += line
        count += item.quantity
        rows.append(
            {
                "food_id": food.id,
                "name": food.name,
                "image": food.image.url if food.image else "",
                "price": f"{food.price:.2f}",
                "quantity": item.quantity,
                "line_total": f"{line:.2f}",
                "available": food.is_available,
            }
        )
    return {"items": rows, "count": count, "total": f"{total:.2f}"}


def order_dict(order, admin=False):
    data = {
        "id": order.id,
        "status": order.status,
        "status_label": order.get_status_display(),
        "total": f"{order.total:.2f}",
        "address": order.address,
        "phone": order.phone,
        "note": order.note,
        "created_at": order.created_at.isoformat(),
        "can_cancel": order.status == STATUS_PENDING,
        "items": [
            {"name": i.name, "price": f"{i.price:.2f}", "quantity": i.quantity}
            for i in order.items.all()
        ],
    }
    if admin:
        data["username"] = order.user.username
        data["next_statuses"] = STATUS_FLOW[order.status]
    return data


# cart
@api(["GET", "POST"], auth="user")
def cart(request):
    if request.method == "GET":
        return JsonResponse({"cart": cart_dict(request.user)})

    data = json_body(request)
    food_id = to_int(data.get("food_id"), "food", minimum=1)
    quantity = to_int(data.get("quantity", 1), "quantity", minimum=1, maximum=MAX_QUANTITY)
    food = get_or_404(Food.objects.filter(is_available=True), pk=food_id)

    item, created = CartItem.objects.get_or_create(
        user=request.user, food=food, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity = min(MAX_QUANTITY, item.quantity + quantity)
        item.save(update_fields=["quantity"])
    return JsonResponse({"cart": cart_dict(request.user)})


@api(["PUT", "DELETE"], auth="user")
def cart_item(request, food_id):
    item = get_or_404(CartItem.objects.filter(user=request.user), food_id=food_id)
    if request.method == "DELETE":
        item.delete()
    else:
        data = json_body(request)
        item.quantity = to_int(data.get("quantity"), "quantity", minimum=1, maximum=MAX_QUANTITY)
        item.save(update_fields=["quantity"])
    return JsonResponse({"cart": cart_dict(request.user)})


# orders
@api(["GET", "POST"], auth="user")
def orders(request):
    if request.method == "GET":
        qs = Order.objects.filter(user=request.user).prefetch_related("items")
        return JsonResponse({"orders": [order_dict(o) for o in qs]})

    data = json_body(request)
    address = str(data.get("address", "")).strip()
    phone = str(data.get("phone", "")).strip()
    note = str(data.get("note", "")).strip()

    errors = {}
    if not 5 <= len(address) <= 255:
        errors["address"] = "Enter your delivery address (5-255 characters)."
    if not PHONE_RE.match(phone):
        errors["phone"] = "Enter a valid phone number."
    if len(note) > 255:
        errors["note"] = "Note must be 255 characters or fewer."
    if errors:
        raise ApiError("Please fix the highlighted fields.", 422, errors)

    with transaction.atomic():
        items = list(
            CartItem.objects.select_for_update().filter(user=request.user).select_related("food")
        )
        if not items:
            raise ApiError("Your cart is empty.", 400)
        unavailable = [i.food.name for i in items if not i.food.is_available]
        if unavailable:
            raise ApiError(
                "These items are no longer available: " + ", ".join(unavailable) + ". Remove them and try again.",
                409,
            )
        # Prices always come from the database, never from the browser.
        total = sum((i.food.price * i.quantity for i in items), Decimal("0"))
        order = Order.objects.create(
            user=request.user, total=total, address=address, phone=phone, note=note
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(order=order, food=i.food, name=i.food.name, price=i.food.price, quantity=i.quantity)
                for i in items
            ]
        )
        CartItem.objects.filter(user=request.user).delete()

    order = Order.objects.prefetch_related("items").get(pk=order.pk)
    return JsonResponse({"order": order_dict(order)}, status=201)


@api(["POST"], auth="user")
def cancel_order(request, order_id):
    order = get_or_404(Order.objects.filter(user=request.user), pk=order_id)
    if order.status != STATUS_PENDING:
        raise ApiError("Only pending orders can be cancelled.", 409)
    order.status = STATUS_CANCELLED
    order.save(update_fields=["status"])
    order = Order.objects.prefetch_related("items").get(pk=order.pk)
    return JsonResponse({"order": order_dict(order)})
