
import requests
from django.core.management.base import BaseCommand
from recipes.models import Recipe


class Command(BaseCommand):
    help = "Find possible TheMealDB matches without modifying recipes"

    def handle(self, *args, **options):
        recipes = Recipe.objects.order_by("id")
        session = requests.Session()

        found = 0
        missing = 0
        errors = 0

        for recipe in recipes:
            try:
                response = session.get(
                    "https://www.themealdb.com/api/json/v1/1/search.php",
                    params={"s": recipe.name},
                    timeout=15,
                )
                response.raise_for_status()

                meals = response.json().get("meals") or []

                if meals:
                    found += 1
                    self.stdout.write(
                        f"\n{recipe.name} -> "
                        + ", ".join(
                            meal["strMeal"] for meal in meals[:5]
                        )
                    )
                else:
                    missing += 1
                    self.stdout.write(
                        f"\n{recipe.name} -> NOT FOUND"
                    )

            except (requests.RequestException, ValueError) as error:
                errors += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"\n{recipe.name} -> ERROR: {error}"
                    )
                )

        self.stdout.write("\n--- SUMMARY ---")
        self.stdout.write(f"Total recipes: {recipes.count()}")
        self.stdout.write(f"Recipes with candidates: {found}")
        self.stdout.write(f"Recipes without matches: {missing}")
        self.stdout.write(f"Errors: {errors}")
