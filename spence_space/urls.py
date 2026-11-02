from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("discover/", include("recipes.urls")),
    path("", include("accounts.urls")),
]