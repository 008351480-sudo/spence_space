from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy

urlpatterns = [
    path("admin/", admin.site.urls),

    # Forgot password pages (reset-password.html and new-password.html)
    path(
        "reset-password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/reset-password.html",
            email_template_name="accounts/reset-password-email.txt",
            subject_template_name="accounts/reset-password-subject.txt",
            success_url=reverse_lazy("reset_password_sent"),
        ),
        name="reset_password",
    ),
    path(
        "reset-password/sent/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/reset-password-sent.html"),
        name="reset_password_sent",
    ),
    path(
        "new-password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/new-password.html",
            success_url=reverse_lazy("new_password_done"),
        ),
        name="new_password",
    ),
    path(
        "new-password/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/new-password-done.html"),
        name="new_password_done",
    ),

    path("grocery/", include("grocery.urls")),

    # The fridge app goes first so "/" is My Fridges instead of the old home page.
    path("", include("fridge.urls")),
    path("", include("accounts.urls")),
]

# Lets the dev server show uploaded photos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
