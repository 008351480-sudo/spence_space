from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """
    The login box says "Email / Username", but Django normally only checks
    usernames. If what was typed has an @, look the user up by email instead.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        User = get_user_model()
        if "@" in username:
            user = User.objects.filter(email__iexact=username.strip()).order_by("id").first()
        else:
            user = User.objects.filter(username__iexact=username.strip()).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None