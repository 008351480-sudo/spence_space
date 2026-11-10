from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    The login page asks for an email, but Django normally logs in with a
    username. This lets either one work.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        if "@" in username:
            user = User.objects.filter(email__iexact=username).order_by("id").first()
        else:
            user = User.objects.filter(username__iexact=username).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
