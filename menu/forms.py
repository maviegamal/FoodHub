from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Food

MAX_IMAGE_BYTES = 2 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ["name", "cuisine", "description", "price", "rating", "image", "is_available"]

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_image(self):
        image = self.cleaned_data.get("image")
        # Only validate a new upload; an unchanged existing image is fine.
        if isinstance(image, UploadedFile):
            if image.size > MAX_IMAGE_BYTES:
                raise forms.ValidationError("Image must be 2 MB or smaller.")
            # Django's ImageField already verified it is a real image with Pillow.
            fmt = getattr(getattr(image, "image", None), "format", None)
            if fmt not in ALLOWED_FORMATS:
                raise forms.ValidationError("Use a JPEG, PNG or WebP image.")
        return image
