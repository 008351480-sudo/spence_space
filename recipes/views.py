from django.shortcuts import render
from .models import Recipe


def discover(request):
    recipes = Recipe.objects.all().order_by("name")

    return render(
        request,
        "recipes/discover.html",
        {"recipes": recipes}
    )