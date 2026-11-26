import uuid
from decimal import Decimal

from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def food_image_path(instance, filename):
    """Random file names: never trust the uploaded name."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    if ext not in ALLOWED_EXTENSIONS:
        ext = "jpg"
    return f"foods/{uuid.uuid4().hex}.{ext}"


class Food(models.Model):
    name = models.CharField(max_length=120)
    cuisine = models.CharField(max_length=60)
    description = models.TextField(validators=[MaxLengthValidator(1000)])
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))],
    )
    image = models.ImageField(upload_to=food_image_path)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
