from django.http import JsonResponse

from core.api import ApiError, api, get_or_404

from .forms import FoodForm
from .models import Food


def food_dict(food):
    return {
        "id": food.id,
        "name": food.name,
        "cuisine": food.cuisine,
        "description": food.description,
        "price": f"{food.price:.2f}",
        "rating": f"{food.rating:.1f}",
        "image": food.image.url if food.image else "",
        "is_available": food.is_available,
    }


def _form_errors(form):
    return {field: errors[0] for field, errors in form.errors.items()}


@api(["GET"])
def food_list(request):
    foods = Food.objects.filter(is_available=True)
    return JsonResponse({"foods": [food_dict(f) for f in foods]})


@api(["GET", "POST"], auth="admin")
def admin_foods(request):
    if request.method == "GET":
        return JsonResponse({"foods": [food_dict(f) for f in Food.objects.all()]})
    form = FoodForm(request.POST, request.FILES)
    if not form.is_valid():
        raise ApiError("Please fix the highlighted fields.", 422, _form_errors(form))
    food = form.save()
    return JsonResponse({"food": food_dict(food)}, status=201)


@api(["GET", "POST", "DELETE"], auth="admin")
def admin_food_detail(request, food_id):
    """POST updates (multipart), because Django does not parse multipart PUT."""
    food = get_or_404(Food.objects.all(), pk=food_id)

    if request.method == "GET":
        return JsonResponse({"food": food_dict(food)})

    if request.method == "DELETE":
        image = food.image
        food.delete()
        if image:
            image.storage.delete(image.name)
        return JsonResponse({"ok": True})

    old_image = food.image.name
    form = FoodForm(request.POST, request.FILES, instance=food)
    if not form.is_valid():
        raise ApiError("Please fix the highlighted fields.", 422, _form_errors(form))
    food = form.save()
    if old_image and food.image.name != old_image:
        food.image.storage.delete(old_image)
    return JsonResponse({"food": food_dict(food)})
