from django.conf import settings
from django.db import models

MAX_QUANTITY = 20

STATUS_PENDING = "pending"
STATUS_PREPARING = "preparing"
STATUS_OUT = "out_for_delivery"
STATUS_DELIVERED = "delivered"
STATUS_CANCELLED = "cancelled"

STATUS_CHOICES = [
    (STATUS_PENDING, "Pending"),
    (STATUS_PREPARING, "Preparing"),
    (STATUS_OUT, "Out for delivery"),
    (STATUS_DELIVERED, "Delivered"),
    (STATUS_CANCELLED, "Cancelled"),
]

# Which statuses the admin may move an order to next.
STATUS_FLOW = {
    STATUS_PENDING: [STATUS_PREPARING, STATUS_CANCELLED],
    STATUS_PREPARING: [STATUS_OUT, STATUS_CANCELLED],
    STATUS_OUT: [STATUS_DELIVERED, STATUS_CANCELLED],
    STATUS_DELIVERED: [],
    STATUS_CANCELLED: [],
}


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    food = models.ForeignKey("menu.Food", on_delete=models.CASCADE, related_name="+")
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "food"], name="unique_cart_food_per_user")
        ]


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class OrderItem(models.Model):
    """Snapshot of what was bought, so later menu edits don't change old orders."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food = models.ForeignKey("menu.Food", on_delete=models.SET_NULL, null=True, related_name="+")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
