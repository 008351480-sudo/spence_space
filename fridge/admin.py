from django.contrib import admin

from .models import Fridge, Ingredient, SavedRecipe


@admin.register(Fridge)
class FridgeAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "household", "created_at")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "expiration_date", "fridge", "added_by", "added_at")
    list_filter = ("fridge__household",)
    search_fields = ("name", "barcode")


@admin.register(SavedRecipe)
class SavedRecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe_id", "saved_at")
