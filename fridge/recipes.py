"""
The recipes shown on the Discover page.

Each recipe has a list of ingredients so the site can count how many
of them are already in your fridges ("Recipes You Can Make").
"""

FEATURED_RECIPES = [
    {
        "id": "spaghetti",
        "name": "Spaghetti",
        "category": "Italian",
        "image": "images/spaghetti.jpg",
        "ingredients": ["spaghetti", "ground beef", "tomato sauce", "onion", "garlic"],
    },
    {
        "id": "chicken-adobo",
        "name": "Chicken Adobo",
        "category": "Filipino",
        "image": "images/adobo.jpg",
        "ingredients": ["chicken", "soy sauce", "vinegar", "garlic", "bay leaves"],
    },
    {
        "id": "chicken-tacos",
        "name": "Chicken Tacos",
        "category": "Hispanic",
        "image": "images/tacos.jpg",
        "ingredients": ["chicken", "tortillas", "onion", "cilantro", "lime"],
    },
    {
        "id": "cheeseburger",
        "name": "Cheeseburger",
        "category": "American",
        "image": "images/burger.jpg",
        "ingredients": ["ground beef", "buns", "cheese", "lettuce", "tomato"],
    },
    {
        "id": "ramen",
        "name": "Ramen",
        "category": "Japanese",
        "image": "images/ramen.jpg",
        "ingredients": ["ramen noodles", "eggs", "pork", "green onion", "broth"],
    },
    {
        "id": "pad-thai",
        "name": "Pad Thai",
        "category": "Thai",
        "image": "images/pad-thai.jpg",
        "ingredients": ["rice noodles", "shrimp", "eggs", "peanuts", "bean sprouts"],
    },
]

EVERYDAY_RECIPES = [
    {
        "id": "french-toast",
        "name": "French Toast",
        "category": "Breakfast",
        "image": "images/french-toast.jpg",
        "ingredients": ["bread", "eggs", "milk", "butter", "cinnamon"],
    },
    {
        "id": "cheese-omelette",
        "name": "Cheese Omelette",
        "category": "Breakfast",
        "image": "images/omelette.jpg",
        "ingredients": ["eggs", "cheese", "milk", "butter"],
    },
    {
        "id": "grilled-cheese",
        "name": "Grilled Cheese",
        "category": "Lunch",
        "image": "images/grilled-cheese.jpg",
        "ingredients": ["bread", "cheese", "butter"],
    },
]

ALL_RECIPES = FEATURED_RECIPES + EVERYDAY_RECIPES


def get_recipe(recipe_id):
    for recipe in ALL_RECIPES:
        if recipe["id"] == recipe_id:
            return recipe
    return None


def has_ingredient(needed, ingredient_names):
    """
    True if something in the fridge matches. Matches loosely so that
    "Whole Milk" counts as milk and "Cheddar Cheese" counts as cheese.
    """
    for name in ingredient_names:
        if needed in name or name in needed:
            return True
    return False


def recipes_you_can_make(ingredient_names):
    """
    Returns recipes that use at least one thing you have, best matches first.
    Each one gets "have", "total" and "percent" added for the progress bar.
    """
    ingredient_names = [name.lower().strip() for name in ingredient_names if name.strip()]
    results = []

    for recipe in ALL_RECIPES:
        have = sum(1 for needed in recipe["ingredients"] if has_ingredient(needed, ingredient_names))
        if have > 0:
            total = len(recipe["ingredients"])
            results.append({
                **recipe,
                "have": have,
                "total": total,
                "percent": round(have / total * 100, 2),
            })

    results.sort(key=lambda r: r["percent"], reverse=True)
    return results
