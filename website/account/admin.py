from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _("Profile")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    inlines = [ProfileInline]

    list_display = ("pk", "login", "email", "is_staff", "is_active")
    list_display_links = (
        "pk",
        "login",
        "email",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )

    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("login", "email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "created_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "login",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return CustomUser.objects.select_related("profile").prefetch_related(
            "groups", "user_permissions"
        )
