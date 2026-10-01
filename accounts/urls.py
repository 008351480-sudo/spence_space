from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.FridgeLoginView.as_view(), name="login"),
    path("logout/", views.FridgeLogoutView.as_view(), name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]
