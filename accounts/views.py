from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect

from .forms import SignUpForm
from .models import Household, Profile


class FridgeLoginView(LoginView):
    """Handles GET (show form) and POST (authenticate) for /login/."""
    template_name = "accounts/login.html"


class FridgeLogoutView(LogoutView):
    """Logs the user out. Must be triggered via POST (see dashboard.html)."""
    next_page = "login"


def signup_view(request):
    """
    Creates a new User, then either:
      - creates a brand-new Household (user becomes 'owner'), or
      - attaches the user to an existing Household via invite code ('member').
    Logs the user in immediately after successful signup.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            action = form.cleaned_data["household_action"]

            if action == "create":
                household = Household.objects.create(
                    name=form.cleaned_data["household_name"],
                    owner=user,
                )
                Profile.objects.create(user=user, household=household, role="owner")
            else:
                code = form.cleaned_data["invite_code"].upper()
                household = Household.objects.get(invite_code=code)
                Profile.objects.create(user=user, household=household, role="member")

            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def dashboard_view(request):
    """
    Shows the logged-in user's household, its members, and (if they're
    the owner) the invite code to share with family members.
    """
    profile = request.user.profile
    household = profile.household
    members = household.members.select_related("user")

    return render(
        request,
        "accounts/dashboard.html",
        {
            "household": household,
            "members": members,
            "is_owner": profile.role == "owner",
        },
    )

def home_view(request):
    """
    Temporary home page: send logged-in users to their dashboard and everyone else to the login page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")
