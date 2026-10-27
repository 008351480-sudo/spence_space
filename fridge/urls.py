from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_fridges_view, name="my_fridges"),
    path("fridges/add/", views.add_fridge_view, name="add_fridge"),
    path("fridges/<int:fridge_id>/", views.fridge_view, name="fridge"),
    path("fridges/<int:fridge_id>/created/", views.fridge_created_view, name="fridge_created"),
    path("fridges/<int:fridge_id>/stock/", views.fridge_stock_view, name="fridge_stock"),
    path("fridges/<int:fridge_id>/add/", views.add_ingredients_view, name="add_ingredients"),
    path("fridges/<int:fridge_id>/add/manual/", views.manual_ingredients_view, name="manual_ingredients"),
    path("fridges/<int:fridge_id>/add/barcode/", views.scan_barcode_view, name="scan_barcode"),
    path("fridges/<int:fridge_id>/add/receipt/", views.scan_receipt_view, name="scan_receipt"),
    path("fridges/<int:fridge_id>/add/receipt/verify/", views.verify_receipt_view, name="verify_receipt"),
    path("ingredients/<int:ingredient_id>/remove/", views.remove_ingredient_view, name="remove_ingredient"),

    # Used by the JavaScript on the barcode page
    path("barcode/read-photo/", views.read_barcode_photo_view, name="read_barcode_photo"),
    path("barcode/lookup/<str:barcode>/", views.lookup_barcode_view, name="lookup_barcode"),

    path("discover/", views.discover_view, name="discover"),
    path("save-recipe/", views.save_recipe_view, name="save_recipe"),
    path("recipes/", views.my_recipes_view, name="my_recipes"),
    path("recipes/<str:recipe_id>/add-to-grocery-list/", views.add_missing_to_grocery_view, name="add_missing_to_grocery"),
]
