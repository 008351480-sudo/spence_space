from django.db import models
from accounts.models import Household
# Create your models here.
class GroceryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="grocery_items",
    )

    def _str_(self):
        return f"{self.name} ({self.quantity})"

class PurchasedItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="purchased_items",
    )

    def _str_(self):
        return f"{self.name} ({self.quantity})"