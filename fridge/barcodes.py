"""
Barcode helpers for the fridge app.

- read_barcode_from_image(): finds a barcode in an uploaded photo
- lookup_product(): gets the product name/brand/picture from Open Food Facts
"""

import json
import urllib.error
import urllib.request

import zxingcpp
from PIL import Image, ImageOps

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product/{}.json?fields=product_name,brands,image_front_url"


def read_barcode_from_image(image_file):
    """
    Returns the barcode number found in the image, or None if there isn't one.
    Phone pictures are often sideways, so the EXIF rotation gets fixed first.
    """
    try:
        image = Image.open(image_file)
        image = ImageOps.exif_transpose(image).convert("RGB")
    except Exception:
        return None

    # Big phone photos are slow to scan, so shrink them down first.
    image.thumbnail((1600, 1600))

    results = zxingcpp.read_barcodes(image)
    if not results:
        # Try again in black and white, sometimes that helps with glare.
        results = zxingcpp.read_barcodes(ImageOps.grayscale(image))

    if results:
        return results[0].text
    return None


def lookup_product(barcode):
    """
    Looks up a barcode on Open Food Facts (free, no API key).
    Returns a dict with name, brand and image_url, or None if it's not found
    or the site can't be reached.
    """
    if not barcode.isdigit():
        return None

    request = urllib.request.Request(
        OPEN_FOOD_FACTS_URL.format(barcode),
        headers={"User-Agent": "SpenceSpace/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", "").split(",")[0].strip(),
        "image_url": product.get("image_front_url", ""),
    }
