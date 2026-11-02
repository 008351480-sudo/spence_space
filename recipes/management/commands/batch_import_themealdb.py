
from django.core.management.base import BaseCommand
from django.core.management import call_command


# Reviewed recipe matches
APPROVED_RECIPES = {
    "Fried Rice": "Chicken Fried Rice",
    "Tomato Soup": "Creamy Tomato Soup",
    "Corn Soup": "Creamy Corn Soup Recipe",
    "Carrot Cake": "Carrot Cake",
    "Pancakes": "Pancakes",
    "Spaghetti": "Spaghetti Bolognese",
    "Omelet": "French Omelette",
    "Fried Chicken": "Kentucky Fried Chicken",
}


class Command(BaseCommand):
    help = "Batch import selected recipes from TheMealDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--save",
            action="store_true",
            help="Save the recipes to the database"
        )

    def handle(self, *args, **options):
        for recipe_name, meal_name in APPROVED_RECIPES.items():
            self.stdout.write(f"\nChecking {recipe_name}...")

            try:
                call_command(
                    "import_themealdb",
                    recipe=recipe_name,
                    meal=meal_name,
                    save=options["save"],
                )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed {recipe_name}: {error}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("\nBatch finished.")
        )
