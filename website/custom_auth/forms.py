from django import forms
from django.conf import settings
from django.utils.timezone import datetime
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _


from .models import CustomUser
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для регистрации профиля пользователя

    Атрибуты:
        email: электронная почта пользователя (обязательное поле)
        birthday: день рождения пользователя (необязательное поле),
        password1: пароль (обязательное поле)
        password2: подтверждение предыдущего пароля (обязательное поле)
    """

    email = forms.EmailField(
        label="Email",
        required=True
    )
    birthday = forms.DateField(
        label=_("Birthday"),
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"},
        ),
        required=False,
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label="Password Confirm",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "login",
            "email",
            "password1",
            "password2",
            "birthday",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_birthday(self):
        """
        Проверяем дату рождения на корректность

        Если дата рождения позже сегодняшней даты,
        поднимаем исключение forms.ValidationError

        Возвращаем:
            birthday - указанный день рождения пользователя

        Исключения:
            forms.ValidationError - если день рождения позже по дате

        """
        birthday = self.cleaned_data.get("birthday")
        today_date = datetime.today().date()

        if birthday and birthday > today_date:
            raise forms.ValidationError(_("Ваш день рождения не может быть позже сегодняшнего дня"))

        return birthday


class CustomUserChangeForm(UserChangeForm):
    """
    Форма для изменения данных пользователя, включая изменение пароля.

    Эта форма позволяет пользователю изменять свой адрес электронной почты,
    а также задать новый пароль. Она выполняет валидацию старого пароля
    и проверяет, что новый пароль соответствует требованиям безопасности.
    """

    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "old_password",
            "new_password1",
            "new_password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Проверяет старый пароль на корректность.

        Если старый пароль не соответствует тому, что хранится в базе данных,
        вызывается ошибка валидации.

        Returns:
            str: Старый пароль, если он корректен.
        Raises:
            forms.ValidationError: Если старый пароль неверен.
        """
        old_password = self.cleaned_data.get("old_password")
        if not self.instance.check_password(old_password) and old_password:
            raise forms.ValidationError("Старый пароль не верен")
        return old_password

    def clean_new_password1(self):
        """
        Проверяет новый пароль на соответствие требованиям безопасности.
        Если новый пароль не соответствует требованиям, вызывается ошибка валидации.

        Returns:
            str: Новый пароль, если он валиден.
        Raises:
            forms.ValidationError: Если новый пароль не соответствует требованиям.
        """
        new_password1 = self.cleaned_data.get("new_password1")
        if new_password1:
            validate_password(new_password1, self.instance)
        return new_password1

    def clean_new_password2(self):
        """
        Проверяет совпадение нового пароля и его подтверждения.
        Если пароли не совпадают, вызывается ошибка валидации.

        Returns:
            str: Подтвержденный новый пароль, если он валиден.
        Raises:
            forms.ValidationError: Если новый пароль и его подтверждение не совпадают.
        """
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Введенные пароли не совпадают")
        return new_password2

    def save(self, commit=True):
        """
        Сохраняет изменения пользователя.
        Устанавливает новый пароль, если он указан, и сохраняет пользователя
        в базе данных.

        Args:
            commit (bool): Если True, сохраняет изменения в базе данных.
        Returns:
            Custom:User  Объект пользователя с обновленными данными.
        """
        user = super().save(commit=False)
        if self.cleaned_data["new_password1"]:
            user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


class ProfileChangeForm(forms.ModelForm):
    """
    Форма для редактирования профиля
    Эта форма включает поля для редактирования информации о пользователе,
    включая имя, фамилию, отчество, номер телефона и фотографию профиля.

    first_name - имя в профиле
    last_name - фамилия в профиле
    patronymic - отчество в профиле (необязательно)
    phone - номер телефона профиля
    photo - фотография профиля
    """

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "patronymic",
            "phone",
            "photo",
        ]

    def clean_phone(self):
        """
        Проверяет корректность номера телефона.
        Удаляет все символы, кроме цифр, и проверяет, что номер телефона
        содержит 10 цифр. Если номер некорректен, вызывается ошибка валидации.

        Returns:
            str: Нормализованный номер телефона, содержащий 10 цифр.
        Raises:
            forms.ValidationError: Если номер телефона не содержит 10 цифр.
        """
        phone = self.cleaned_data.get("phone")
        if phone:
            # Удаляем все символы, кроме цифр и отрезаем 7
            phone = "".join(filter(str.isdigit, phone))[1:]
            if len(phone) != 10:
                raise forms.ValidationError("Номер телефона должен содержать 10 цифр.")
        return phone

    def clean_first_name(self):
        first_name: str = self.cleaned_data.get("first_name")
        if first_name and (first_name.isdigit() or not all(char.isalpha() for char in first_name)):
            raise forms.ValidationError("В имени не должно быть ни одной цифры!")

        return first_name

    def clean_last_name(self):
        last_name: str = self.cleaned_data.get("last_name")
        if last_name and (last_name.isdigit() or not all(char.isalpha() for char in last_name)):
            raise forms.ValidationError("В фамилии не должно быть ни одной цифры!")

        return last_name

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get("patronymic")
        if patronymic and (patronymic.isdigit() or not all(char.isalpha() for char in patronymic)):
            raise forms.ValidationError("В отчестве не должно быть ни одной цифры!")

        return patronymic

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileRegistrationForm(ProfileChangeForm):
    """
    Форма для регистрации профиля, включающая только ФИО и номер телефона.
    Наследуется от ProfileChangeForm и используется только для начальной регистрации профиля.
    """

    class Meta(ProfileChangeForm.Meta):
        fields = ["first_name", "last_name", "patronymic", "phone"]

    def clean_first_name(self):
        first_name: str = self.cleaned_data.get("first_name")
        if first_name and (first_name.isdigit() or not all(char.isalpha() for char in first_name)):
            raise forms.ValidationError("В имени не должно быть ни одной цифры!")

        return first_name

    def clean_last_name(self):
        last_name: str = self.cleaned_data.get("last_name")
        if last_name and (last_name.isdigit() or not all(char.isalpha() for char in last_name)):
            raise forms.ValidationError("В фамилии не должно быть ни одной цифры!")

        return last_name

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get("patronymic")
        if patronymic and (patronymic.isdigit() or not all(char.isalpha() for char in patronymic)):
            raise forms.ValidationError("В отчестве не должно быть ни одной цифры!")

        return patronymic


class SettingsForm(forms.Form):
    RUSSIAN = "ru"
    ENGLISH = "en"
    LANGUAGES = [
        (RUSSIAN, _("Русский")),
        (ENGLISH, _("Английский")),
    ]

    UTC = "UTC"
    MOSCOW = "Europe/Moscow"
    NEW_YORK = "America/New_York"
    LONDON = "Europe/London"
    TIME_ZONES = [
        (MOSCOW, _("Москва")),
        (UTC, _("Всемирное время")),
        (NEW_YORK, _("Нью-Йорк")),
        (LONDON, _("Лондон")),
    ]

    debug = forms.BooleanField(label=_("Режим отладки"), initial=settings.DEBUG, required=False)
    language = forms.ChoiceField(choices=LANGUAGES, initial=settings.LANGUAGE_CODE)
    timezone = forms.ChoiceField(choices=TIME_ZONES, initial=settings.TIME_ZONE)
    session_age = forms.IntegerField(label=_("Время жизни сессии"), initial=settings.SESSION_COOKIE_AGE)
    email_host = forms.CharField(label=_("HOST электронной почты"), initial=settings.EMAIL_HOST)
    email_tls = forms.BooleanField(label=_("Использование TLS"), initial=settings.EMAIL_USE_TLS, required=False)
    email_port = forms.IntegerField(label=_("PORT электронной почты"), initial=settings.EMAIL_PORT)