
import json
import re
import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient, RecipeIngredient


USER_AGENT = "SpenceSpaceRecipeImporter/1.0"
HEADERS = {"User-Agent": USER_AGENT}

UNITS = {
    "cup", "cups", "tbsp", "tablespoon", "tablespoons",
    "tsp", "teaspoon", "teaspoons", "oz", "ounce", "ounces",
    "lb", "lbs", "pound", "pounds", "g", "kg", "ml",
    "l", "clove", "cloves", "can", "cans",
    "piece", "pieces", "pinch", "pinches"
}


def find_recipe(data):
    if isinstance(data, list):
        for item in data:
            result = find_recipe(item)
            if result:
                return result

    if isinstance(data, dict):
        types = data.get("@type", [])
        if isinstance(types, str):
            types = [types]

        if any(str(t).split("/")[-1] == "Recipe" for t in types):
            return data

        for key in ("@graph", "mainEntity"):
            if key in data:
                result = find_recipe(data[key])
                if result:
                    return result

    return None


def parse_duration(value):
    if not value:
        return None

    match = re.fullmatch(
        r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        str(value),
        re.I
    )
    if not match:
        return None

    hours, minutes, seconds = match.groups()
    total = (
        int(hours or 0) * 60
        + int(minutes or 0)
        + (int(seconds or 0) + 59) // 60
    )
    return total


def parse_servings(value):
    if isinstance(value, list):
        value = value[0] if value else None
    if value is None:
        return None

    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


def parse_ingredient(text):
    text = str(text).strip()

    pattern = (
        r"^(\d+(?:\.\d+)?|\d+/\d+)"
        r"(?:\s+(\d+/\d+))?"
        r"\s*(.*)$"
    )

    match = re.match(pattern, text)

    if not match:
        return text, None, ""

    first, second, remainder = match.groups()

    def number(value):
        if "/" in value:
            a, b = value.split("/")
            return Decimal(a) / Decimal(b)
        return Decimal(value)

    try:
        quantity = number(first)
        if second:
            quantity += number(second)
    except (InvalidOperation, ZeroDivisionError):
        return text, None, ""

    words = remainder.split()
    unit = ""

    if words and words[0].lower().rstrip(".") in UNITS:
        unit = words.pop(0)

    name = " ".join(words).strip()
    if not name:
        return text, None, ""

    return name[:200], quantity, unit


def image_url(value):
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        value = value.get("url") or value.get("contentUrl") or ""
    return str(value or "")[:1000]


def description_text(value):
    if isinstance(value, dict):
        value = value.get("text", "")
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    return BeautifulSoup(str(value or ""), "html.parser").get_text(
        " ", strip=True
    )


class Command(BaseCommand):
    help = "Fetch structured recipe metadata and ingredients"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, default=0)

    def handle(self, *args, **options):
        recipes = Recipe.objects.exclude(source_url="").order_by("id")

        if options["limit"] > 0:
            recipes = recipes[:options["limit"]]

        success = 0
        failed = 0

        session = requests.Session()
        session.headers.update(HEADERS)
        robots_cache = {}

        for recipe in recipes:
            self.stdout.write(f"Checking: {recipe.name}")

            try:
                parsed = urlparse(recipe.source_url)
                origin = f"{parsed.scheme}://{parsed.netloc}"

                if origin not in robots_cache:
                    robots = RobotFileParser()
                    robots.set_url(origin + "/robots.txt")
                    try:
                        robots.read()
                        robots_cache[origin] = robots

                    except Exception as error:
                        robots_cache[origin] = None
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not retrieve robots.txt: {error}"
                            )
                        )

                if robots is None:
                    raise ValueError("Could not verify robots.txt")

                if not robots.can_fetch(USER_AGENT, recipe.source_url):
                    raise ValueError(
                        "Automated access disallowed or not confirmed"
                    )

                response = session.get(
                    recipe.source_url,
                    timeout=15
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                structured = None

                for script in soup.find_all(
                    "script", type="application/ld+json"
                ):
                    try:
                        data = json.loads(script.string or script.get_text())
                        structured = find_recipe(data)
                        if structured:
                            break
                    except (ValueError, TypeError):
                        continue

                if not structured:
                    raise ValueError("No structured Recipe data")

                raw_ingredients = structured.get("recipeIngredient", [])
                if isinstance(raw_ingredients, str):
                    raw_ingredients = [raw_ingredients]

                if not options["dry_run"]:
                    from django.db import transaction

                    with transaction.atomic():
                        recipe.prep_time = (
                            parse_duration(structured.get("prepTime"))
                            or recipe.prep_time
                        )
                        recipe.cook_time = (
                            parse_duration(structured.get("cookTime"))
                            or recipe.cook_time
                        )
                        recipe.servings = (
                            parse_servings(structured.get("recipeYield"))
                            or recipe.servings
                        )
                        recipe.image_url = (
                            image_url(structured.get("image"))
                            or recipe.image_url
                        )

                        # Keep original third-party instructions
                        # and descriptions on their source websites.
                        recipe.save()

                        for raw in raw_ingredients:
                            name, quantity, unit = parse_ingredient(raw)
                            if not name:
                                continue

                            ingredient, _ = Ingredient.objects.get_or_create(
                                name=name
                            )

                            RecipeIngredient.objects.get_or_create(
                                recipe=recipe,
                                ingredient=ingredient,
                                defaults={
                                    "quantity": quantity,
                                    "unit": unit[:50]
                                }
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found {len(raw_ingredients)} ingredients"
                    )
                )
                success += 1

            except Exception as error:
                failed += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped {recipe.name}: {error}"
                    )
                )

            time.sleep(2)

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Success: {success}, Failed: {failed}"
            )
        )
