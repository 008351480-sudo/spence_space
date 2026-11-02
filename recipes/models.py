
from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    source_url = models.URLField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    prep_time = models.PositiveIntegerField(null=True, blank=True)
    cook_time = models.PositiveIntegerField(null=True, blank=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    image_url = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit = models.CharField(max_length=50, blank=True)
    measurement = models.CharField(
            max_length=150,
            blank=True
        )

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name}"
