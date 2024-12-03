from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Profile
from .forms import ProfileRegistrationForm


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="super@user.com", password="foo", is_superuser=False)


class TestProfile(TestCase):
    def test_create_profile_with_superuser(self):
        """ Тест создания профиля суперпользователя """
        User = get_user_model()
        superuser = User.objects.create_superuser(
            email="admin@mail.ru",
            password="admin"
        )
        self.assertTrue(
            Profile.objects.filter(user=superuser).exists(),
            "Профиль суперпользователя создан успешно!"
        )

    def test_profile_first_name_registration_success(self):
        """
        Успешный тест имени на форме ProfileRegistrationForm
        Поле first_name (имя) не должно содержать ни одной цифры

        """
        form = ProfileRegistrationForm(data={"first_name": "Triangolo"})
        form.is_valid()
        first_name = form.cleaned_data["first_name"]
        self.assertIsInstance(
            first_name,
            str,
            "Поле first_name является инстансом строки"
        )

    def test_profile_first_name_registration_fail(self):
        """
        Неуспешный тест имени на форме ProfileRegistrationForm
        Поле first_name (имя) содержит минимум одну цифру

        """
        form = ProfileRegistrationForm(data={"first_name": 1234567890})
        form.is_valid()
        first_name = form.cleaned_data.get("first_name")
        self.assertIsNone(
            first_name,
            "Поле first_name не прошло валидацию!"
        )

    def test_profile_last_name_registration_success(self):
        """
        Успешный тест фамилии на форме ProfileRegistrationForm
        Поле last_name (фамилия) не содержит ни одной цифры

        """
        form = ProfileRegistrationForm(data={"last_name": "Deer"})
        form.is_valid()
        last_name = form.cleaned_data["last_name"]
        self.assertIsInstance(
            last_name,
            str,
            "Поле last_name является инстансом строки"
        )

    def test_profile_last_name_registration_fail(self):
        """
        Неуспешный тест фамилии на форме ProfileRegistrationForm
        Поле last_name (фамилия) содержит минимум одну цифру

        """
        form = ProfileRegistrationForm(data={"last_name": "3riangolo"})
        form.is_valid()
        last_name = form.cleaned_data.get("last_name")
        self.assertIsNone(
            last_name,
            "Поле last_name не прошло валидацию!"
        )

    def test_profile_patronymic_registration_success(self):
        """
        Успешный тест отчества на форме ProfileRegistrationForm
        Поле patronymic (отчество) не содержит ни одной цифры

        """
        form = ProfileRegistrationForm(data={"patronymic": "Петрович"})
        form.is_valid()
        patronymic = form.cleaned_data["patronymic"]
        self.assertIsInstance(
            patronymic,
            str,
            "Поле patronymic является инстансом строки"
        )

    def test_profile_patronymic_registration_fail(self):
        """
        Неуспешный тест отчества на форме ProfileRegistrationForm
        Поле patronymic (отчество) содержит минимум одну цифру

        """
        form = ProfileRegistrationForm(data={"patronymic": "Петрович2"})
        form.is_valid()
        patronymic = form.cleaned_data.get("patronymic")
        self.assertIsNone(
            patronymic,
            "Поле patronymic не прошло валидацию!"
        )
