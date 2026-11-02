
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from recipes.models import Recipe, Ingredient, RecipeIngredient


class Command(BaseCommand):
    help = "Import Egg Drop Soup details from TheMealDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--recipe",
            type=str,
            default="Egg Drop Soup",
            help="Name of the existing Spence Space recipe"
        )
        parser.add_argument(
            "--meal",
            type=str,
            default=None,
            help="Name of the matching TheMealDB recipe"
        )
        parser.add_argument(
            "--save",
            action="store_true",
            help="Save the recipe to the database"
        )

    def handle(self, *args, **options):
        recipe_name = options["recipe"]
        meal_name = options["meal"] or recipe_name

        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                params={"s": meal_name},
                timeout=15,
            )
            response.raise_for_status()
            meals = response.json().get("meals") or []
        except (requests.RequestException, ValueError) as error:
            raise CommandError(f"API request failed: {error}")

        meal = next(
            (
                item for item in meals
                if item["strMeal"].casefold() == meal_name.casefold()
            ),
            None,
        )

        if meal is None:
            raise CommandError("No exact recipe match found.")

        ingredients = []

        for i in range(1, 21):
            name = (meal.get(f"strIngredient{i}") or "").strip()
            measurement = (meal.get(f"strMeasure{i}") or "").strip()

            if name:
                ingredients.append((name, measurement))

        self.stdout.write(f"Recipe: {meal['strMeal']}")
        self.stdout.write(f"Ingredients: {len(ingredients)}")

        for name, measurement in ingredients:
            self.stdout.write(f"  - {measurement} {name}")

        if not options["save"]:
            self.stdout.write(
                self.style.WARNING(
                    "Preview only. Add --save to import."
                )
            )
            return

        with transaction.atomic():
            try:
                recipe = Recipe.objects.get(name=recipe_name)
            except Recipe.DoesNotExist:
                raise CommandError(
                    "Egg Drop Soup was not found in your database."
                )
            except Recipe.MultipleObjectsReturned:
                raise CommandError(
                    "Multiple Egg Drop Soup records found."
                )

            # Preserve the existing recipe record.
            recipe.instructions = meal.get("strInstructions") or ""
            recipe.image_url = meal.get("strMealThumb") or ""

            recipe.source_url = (
                f"https://www.themealdb.com/meal/{meal['idMeal']}"
            )

            # Keep prep time, cook time and servings unchanged.
            recipe.save(
                update_fields=["instructions", "image_url", "source_url"]
            )

            # Replace ingredient associations for this recipe only.
            recipe.recipe_ingredients.all().delete()

            for name, measurement in ingredients:
                ingredient = Ingredient.objects.filter(
                    name__iexact=name
                ).first()

                if ingredient is None:
                    ingredient = Ingredient.objects.create(name=name)

                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    measurement=measurement,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"{recipe_name} imported successfully!"
            )
        )
