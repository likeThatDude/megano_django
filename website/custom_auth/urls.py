from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from .views import LogInView
from .views import LogOutView
from .views import PersonalCabinet
from .views import ProfileOrdersView
from .views import ProfileView
from .views import ViewedListView
from .views import RegisterView
from .views import UserPasswordResetConfirmView

app_name = "custom_auth"

urlpatterns = [
    path("login/", LogInView.as_view(), name="login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("viewed/", ViewedListView.as_view(), name="viewed-list"),
    path("personal_cabinet/", PersonalCabinet.as_view(), name="personal-cabinet"),
    path("profile_orders/", ProfileOrdersView.as_view(), name="profile-orders"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="custom_auth/password_reset.html",
            email_template_name="account/password_reset_email.html",
            success_url=reverse_lazy("account:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="custom_auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="custom_auth/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
