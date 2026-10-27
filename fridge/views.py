from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .barcodes import lookup_product, read_barcode_from_image
from .forms import BarcodePhotoForm, FridgeForm, IngredientForm, ReceiptForm
from .models import Fridge, Ingredient, SavedRecipe
from grocery.models import GroceryItem

from .recipes import ALL_RECIPES, FEATURED_RECIPES, get_recipe, has_ingredient, recipes_you_can_make


def get_household(request):
    return request.user.profile.household


def get_fridge(request, fridge_id):
    """Gets a fridge, but only if it belongs to the logged-in user's household."""
    return get_object_or_404(Fridge, id=fridge_id, household=get_household(request))


# ---------- My Fridges ----------

@login_required
def my_fridges_view(request):
    """index.html - the list of the household's refrigerators."""
    fridges = get_household(request).fridges.all()
    return render(request, "fridge/index.html", {"fridges": fridges})


@login_required
def add_fridge_view(request):
    """add-fridge.html - creates a new refrigerator."""
    if request.method == "POST":
        form = FridgeForm(request.POST)
        if form.is_valid():
            fridge = form.save(commit=False)
            fridge.household = get_household(request)
            fridge.save()
            return redirect("fridge_created", fridge_id=fridge.id)
    else:
        form = FridgeForm()

    return render(
        request,
        "fridge/add-fridge.html",
        {"form": form, "locations": Fridge.LOCATION_CHOICES},
    )


@login_required
def fridge_created_view(request, fridge_id):
    """fridge-created.html - shown right after making a fridge."""
    return render(request, "fridge/fridge-created.html", {"fridge": get_fridge(request, fridge_id)})


@login_required
def fridge_view(request, fridge_id):
    """fridge.html - the options for one refrigerator."""
    return render(request, "fridge/fridge.html", {"fridge": get_fridge(request, fridge_id)})


@login_required
def fridge_stock_view(request, fridge_id):
    """fridge-stock.html - everything in the fridge."""
    fridge = get_fridge(request, fridge_id)
    return render(
        request,
        "fridge/fridge-stock.html",
        {"fridge": fridge, "ingredients": fridge.ingredients.all()},
    )


@login_required
@require_POST
def remove_ingredient_view(request, ingredient_id):
    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        fridge__household=get_household(request),
    )
    fridge_id = ingredient.fridge_id
    if ingredient.photo:
        ingredient.photo.delete(save=False)
    ingredient.delete()
    messages.success(request, f"Removed {ingredient.name}.")
    return redirect("fridge_stock", fridge_id=fridge_id)


# ---------- Adding ingredients ----------

@login_required
def add_ingredients_view(request, fridge_id):
    """add-ingredients.html - pick receipt, barcode or manual."""
    return render(request, "fridge/add-ingredients.html", {"fridge": get_fridge(request, fridge_id)})


def save_ingredient(request, fridge, template):
    """
    Shared by the manual page and the barcode page since they save
    the same thing. Returns the response to send back.
    """
    if request.method == "POST":
        form = IngredientForm(request.POST, request.FILES)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.fridge = fridge
            ingredient.added_by = request.user
            ingredient.save()
            messages.success(request, f"Added {ingredient.name} to {fridge.name}.")
            return redirect("fridge_stock", fridge_id=fridge.id)
    else:
        form = IngredientForm()

    return render(request, template, {"fridge": fridge, "form": form})


@login_required
def manual_ingredients_view(request, fridge_id):
    """manual-ingredients.html"""
    return save_ingredient(request, get_fridge(request, fridge_id), "fridge/manual-ingredients.html")


@login_required
def scan_barcode_view(request, fridge_id):
    """
    scan-barcode.html - the camera scanning happens in the browser.
    Barcode photos and product lookups get sent to the two views below.
    """
    return save_ingredient(request, get_fridge(request, fridge_id), "fridge/scan-barcode.html")


@login_required
@require_POST
def read_barcode_photo_view(request):
    """Reads the barcode out of an uploaded picture (in Python, with zxing-cpp)."""
    form = BarcodePhotoForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"error": "That file isn't a picture."}, status=400)

    code = read_barcode_from_image(form.cleaned_data["barcode_photo"])
    if not code:
        return JsonResponse({"error": "Couldn't find a barcode in that photo. Try getting closer."}, status=404)
    return JsonResponse({"barcode": code})


@login_required
@require_GET
def lookup_barcode_view(request, barcode):
    """Looks up a barcode on Open Food Facts and returns the product name."""
    product = lookup_product(barcode)
    if not product or not product["name"]:
        return JsonResponse({"barcode": barcode, "found": False})
    return JsonResponse({"barcode": barcode, "found": True, **product})


@login_required
def scan_receipt_view(request, fridge_id):
    """scan-receipt.html - step 1, upload the receipt picture."""
    fridge = get_fridge(request, fridge_id)

    if request.method == "POST":
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            # Reading the items off the receipt isn't built yet,
            # so for now the next page lets you type them in.
            return redirect("verify_receipt", fridge_id=fridge.id)
        messages.error(request, "Please choose a picture of your receipt.")

    return render(request, "fridge/scan-receipt.html", {"fridge": fridge})


@login_required
def verify_receipt_view(request, fridge_id):
    """verify-receipt.html - step 2, check the items and add them all at once."""
    fridge = get_fridge(request, fridge_id)

    if request.method == "POST":
        names = request.POST.getlist("ingredient[]")
        quantities = request.POST.getlist("quantity[]")
        expirations = request.POST.getlist("expiration[]")

        added = 0
        for name, quantity, expiration in zip(names, quantities, expirations):
            name = name.strip()
            if not name:
                continue
            form = IngredientForm({"name": name, "quantity": quantity or 1, "expiration_date": expiration})
            if form.is_valid():
                ingredient = form.save(commit=False)
                ingredient.fridge = fridge
                ingredient.added_by = request.user
                ingredient.save()
                added += 1

        if added:
            messages.success(request, f"Added {added} ingredient(s) to {fridge.name}.")
            return redirect("fridge_stock", fridge_id=fridge.id)
        messages.error(request, "Type in at least one ingredient.")

    return render(request, "fridge/verify-receipt.html", {"fridge": fridge, "rows": range(5)})


# ---------- Recipes ----------

@login_required
def discover_view(request):
    """discover.html - featured recipes and the ones you can make with what you have."""
    household = get_household(request)
    ingredient_names = Ingredient.objects.filter(fridge__household=household).values_list("name", flat=True)

    featured = FEATURED_RECIPES
    can_make = recipes_you_can_make(ingredient_names)

    search = request.GET.get("search", "").strip().lower()
    cuisine = request.GET.get("cuisine", "")
    if search:
        featured = [r for r in ALL_RECIPES if search in r["name"].lower() or search in r["category"].lower()]
        can_make = [r for r in can_make if search in r["name"].lower() or search in r["category"].lower()]
    elif cuisine:
        featured = [r for r in ALL_RECIPES if r["category"] == cuisine]
        can_make = [r for r in can_make if r["category"] == cuisine]

    saved_ids = set(request.user.saved_recipes.values_list("recipe_id", flat=True))

    return render(
        request,
        "fridge/discover.html",
        {
            "featured": featured,
            "can_make": can_make,
            "saved_ids": saved_ids,
            "search": request.GET.get("search", ""),
            "cuisine": cuisine,
            "cuisines": ["Italian", "Filipino", "Hispanic", "Mediterranean", "American", "Nigerian", "Soul Food", "Thai"],
        },
    )


@login_required
@require_POST
def save_recipe_view(request):
    """The heart button. Saves the recipe, or unsaves it if it was already saved."""
    recipe_id = request.POST.get("recipe_id", "")
    recipe = get_recipe(recipe_id)

    if recipe:
        saved = SavedRecipe.objects.filter(user=request.user, recipe_id=recipe_id)
        if saved.exists():
            saved.delete()
        else:
            SavedRecipe.objects.create(user=request.user, recipe_id=recipe_id)

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("discover")


@login_required
def my_recipes_view(request):
    """recipes.html - the recipes you hearted."""
    saved_ids = request.user.saved_recipes.values_list("recipe_id", flat=True)
    recipes = [get_recipe(recipe_id) for recipe_id in saved_ids]
    recipes = [r for r in recipes if r]
    return render(
        request,
        "fridge/recipes.html",
        {"recipes": recipes, "saved_ids": set(saved_ids)},
    )


@login_required
@require_POST
def add_missing_to_grocery_view(request, recipe_id):
    """
    The "+ Grocery List" button on Recipes You Can Make. Puts the
    ingredients you don't have yet onto the household grocery list.
    """
    recipe = get_recipe(recipe_id)
    if not recipe:
        return redirect("discover")

    household = get_household(request)
    have = [name.lower() for name in Ingredient.objects.filter(fridge__household=household).values_list("name", flat=True)]
    missing = [needed for needed in recipe["ingredients"] if not has_ingredient(needed, have)]

    for name in missing:
        # Same as the grocery page: if it's already on the list, don't add it twice
        if not GroceryItem.objects.filter(name__iexact=name, household=household).exists():
            GroceryItem.objects.create(name=name.title(), quantity=1, household=household)

    if missing:
        messages.success(request, f"Added {len(missing)} item(s) for {recipe['name']} to your grocery list.")
    else:
        messages.success(request, f"You already have everything for {recipe['name']}.")

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("discover")
