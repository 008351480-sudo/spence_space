from django.urls import path
from . import views

urlpatterns = [
    path("", views.grocery_list, name="grocery_list"),
    path("remove/<int:item_id>/", views.remove_item, name="remove_item"),
    path("update/<int:item_id>/", views.update_quantity, name="update_quantity"),
    path("bought/<int:item_id>/", views.mark_bought, name="mark_bought"),
    path("add-again/<int:item_id>/", views.add_again, name="add_again"),
]
