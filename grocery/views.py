from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import GroceryItemForm
from .models import GroceryItem, PurchasedItem

@login_required
def grocery_list(request):
    household = request.user.profile.household

    items = GroceryItem.objects.filter(household=household)
    purchased_items = PurchasedItem.objects.filter(household=household)

    if request.method == "POST":
        form = GroceryItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.household = household
            item.save()

            return redirect("grocery_list")

    else:
        form = GroceryItemForm()

    return render(
        request,
        "grocery/grocery_list.html",
        {
            "form": form,
            "items": items,
            "purchased_items": purchased_items,
        },
    )


@login_required
def remove_item(request, item_id):
    household = request.user.profile.household

    item = get_object_or_404(
        GroceryItem,
        id=item_id,
        household=household
    )

    if request.method == "POST":
        item.delete()

    return redirect("grocery_list")

@login_required
def update_quantity(request, item_id):
    household = request.user.profile.household

    item = get_object_or_404(
        GroceryItem,
        id=item_id,
        household=household
    )

    if request.method == "POST":
        quantity = request.POST.get("quantity")

        if quantity:
            item.quantity = quantity
            item.save()

    return redirect("grocery_list")

@login_required
def mark_bought(request, item_id):
    household = request.user.profile.household

    item = get_object_or_404(
        GroceryItem,
        id=item_id,
        household=household
    )

    if request.method == "POST":
        PurchasedItem.objects.create(
            name=item.name,
            quantity=item.quantity,
            household=household
        )

        item.delete()

    return redirect("grocery_list")

@login_required
def add_again(request, item_id):
    household = request.user.profile.household

    purchased_item = get_object_or_404(
        PurchasedItem,
        id=item_id,
        household=household
    )

    if request.method == "POST":

        existing_item = GroceryItem.objects.filter(
            name=purchased_item.name,
            household=household
        ).first()

        if existing_item:
            existing_item.quantity += purchased_item.quantity
            existing_item.save()

        else:
            GroceryItem.objects.create(
                name=purchased_item.name,
                quantity=purchased_item.quantity,
                household=household
        )

    return redirect("grocery_list")





