import uuid

from django.conf import settings
from django.db import models


class Household(models.Model):
    """
    A shared account that can contain multiple users (e.g. a family).
    All members of a Household will eventually share the same fridge(s),
    inventory, and grocery list data.
    """

    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=8, unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_households",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self._generate_unique_invite_code()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_unique_invite_code(cls):
        while True:
            code = uuid.uuid4().hex[:8].upper()
            if not cls.objects.filter(invite_code=code).exists():
                return code

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Extends Django's built-in User model with a link to a Household.
    This is what lets one 'account' (household) have multiple family
    members logging in with their own separate username/password.
    """

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("member", "Member"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="members",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")

    def __str__(self):
        return f"{self.user.username} ({self.household.name} - {self.role})"
