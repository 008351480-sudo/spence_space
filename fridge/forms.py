from django import forms

from .models import Fridge, Ingredient


class FridgeForm(forms.ModelForm):
    class Meta:
        model = Fridge
        fields = ["name", "location"]


class IngredientForm(forms.ModelForm):
    """Used by both the Add Manually page and the Scan Barcode page."""

    class Meta:
        model = Ingredient
        fields = ["name", "quantity", "expiration_date", "barcode", "photo", "image_url"]

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity has to be at least 1.")
        return quantity


class BarcodePhotoForm(forms.Form):
    """A picture of a barcode, for when the camera isn't working."""

    barcode_photo = forms.ImageField()


class ReceiptForm(forms.Form):
    receipt = forms.ImageField()
