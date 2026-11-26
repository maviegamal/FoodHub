from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from menu.models import Food

SAMPLES = [
    ("Margherita Pizza", "Italian", "Classic tomato, mozzarella and fresh basil on a thin crust.", "11.50", "4.7", (214, 69, 65)),
    ("Chicken Shawarma Wrap", "Middle Eastern", "Grilled chicken, garlic sauce and pickles in warm flatbread.", "8.00", "4.6", (230, 126, 34)),
    ("Beef Burger", "American", "Juicy beef patty, cheddar, lettuce and house sauce.", "10.00", "4.5", (150, 90, 50)),
    ("Veggie Pad Thai", "Thai", "Rice noodles stir-fried with vegetables, peanuts and lime.", "9.50", "4.4", (39, 174, 96)),
    ("Salmon Sushi Set", "Japanese", "Eight pieces of fresh salmon nigiri with soy and wasabi.", "14.00", "4.8", (52, 152, 219)),
]


def make_image(title, color):
    """Placeholder picture so the site works offline. The admin can replace it."""
    image = Image.new("RGB", (800, 600), color)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default(size=44)
    except TypeError:
        font = ImageFont.load_default()
    draw.text((40, 260), title, fill=(255, 255, 255), font=font)
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Add a few sample foods (skips ones that already exist)."

    def handle(self, *args, **options):
        created = 0
        for name, cuisine, description, price, rating, color in SAMPLES:
            if Food.objects.filter(name=name).exists():
                continue
            food = Food(
                name=name,
                cuisine=cuisine,
                description=description,
                price=Decimal(price),
                rating=Decimal(rating),
            )
            food.image.save("sample.jpg", make_image(name, color), save=False)
            food.save()
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Added {created} sample food(s)."))
