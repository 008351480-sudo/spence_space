from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import Household


class Fridge(models.Model):
    """
    A refrigerator that belongs to a household. Everyone in the household
    can see it and add ingredients to it.
    """

    LOCATION_CHOICES = [
        ("Kitchen", "Kitchen"),
        ("Bedroom", "Bedroom"),
        ("Garage", "Garage"),
        ("Backyard", "Backyard"),
        ("Other", "Other"),
    ]

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="fridges",
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="Kitchen")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} ({self.location})"


class Ingredient(models.Model):
    """
    One ingredient stored in a fridge. Can be added by hand, by scanning
    a barcode, or from a receipt, and can have a photo uploaded for it.
    """

    fridge = models.ForeignKey(
        Fridge,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    expiration_date = models.DateField(null=True, blank=True)
    barcode = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to="ingredient_photos/", blank=True)
    # Picture from the barcode lookup, used when no photo was uploaded.
    image_url = models.URLField(max_length=500, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ingredients_added",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expiration_date", "name"]

    def picture(self):
        """Returns the uploaded photo if there is one, otherwise the lookup image."""
        if self.photo:
            return self.photo.url
        return self.image_url

    def is_expired(self):
        return self.expiration_date is not None and self.expiration_date < timezone.localdate()

    def __str__(self):
        return f"{self.name} x{self.quantity} ({self.fridge.name})"


class SavedRecipe(models.Model):
    """A recipe someone hearted on the Discover page. Shows up in My Recipes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_recipes",
    )
    recipe_id = models.CharField(max_length=50)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe_id"], name="unique_saved_recipe"),
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.recipe_id}"
