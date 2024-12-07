from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
from .utils import profile_photo_directory_path
from .utils import validate_avatar_size


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Изменённая модель пользователя, с которым завязаны все действия по
    регистрации, аутентификации и авторизации.

    Attributes:
        login: login пользователя;
        email: email пользователя;
        created_at: дата регистрации пользователя;
        is_staff: Логическое значение - является ли пользователь администратором;
        is_active: Логическое значение - для "мягкого" удаления пользователя.
    """

    login = models.CharField(max_length=50, unique=True, verbose_name=_("Login"))
    email = models.EmailField(unique=True, verbose_name=_("Email"), db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created at"))
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Staff status"),
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text="Designates whether this user should be treated as active."
        " Unselect this instead of deleting accounts.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["login"]

    objects = CustomUserManager()

    class Meta:
        app_label = "custom_auth"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ("login",)

    def __str__(self):
        """Возвращаем никнейм пользователя, если он имеется"""
        return self.login if self.login else "Anonymous"


class Profile(models.Model):
    """
    Модель для дополнительной информации пользователя.

    Attributes:
        user: связь к пользователю по типу связи один-к-одному
        first_name: имя пользователя;
        last_name: фамилия пользователя;
        patronymic: отчество (при наличии)
        address: адрес пользователя;
        phone: номер телефона пользователя;
        photo: фото/аватар пользователя.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="profile",
    )
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Firstname"))
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Lastname"))
    patronymic = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Patronymic"))
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Address"))
    phone = models.CharField(
        unique=True,
        max_length=18,
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        upload_to=profile_photo_directory_path,
        verbose_name=_("Photo"),
        validators=[validate_avatar_size],
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "custom_auth"
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = (
            "first_name",
            "last_name",
        )

    def __str__(self):
        """Возвращаем имя профиля, если оно имеется"""
        return self.first_name if self.first_name else f"Имя профиля №{self.pk}"
