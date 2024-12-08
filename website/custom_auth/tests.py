from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile
from .forms import ProfileRegistrationForm
from .forms import CustomUserChangeForm


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
    @classmethod
    def setUpClass(cls):
        """
        В начале, создаем пользователя
        и проверяем создали ли мы профиль для него

        """
        super().setUpClass()
        cls.credentials: dict[str, str] = {
            "login": "admin",
            "email": "admin@gmail.com",
            "password": "admin"
        }
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(**cls.credentials)

    def test_user_creation_form_profile(self):
        """
        Тест формы CustomUserCreationForm - создание профиля пользователя

        Для теста требуется:
            - запустить сервер Redis командой `redis-server`
            - запустить асинхронную очередь задач Celery командой
                `python -m celery -A website worker -l info` в папке проекта

        """
        data: dict[str, str] = {
            "login": "user_nickname",
            "email": "user_email@gmail.com",
            "password1": "user_password",
            "password2": "user_password",
            "first_name": "Николай",
            "last_name": "Николаенко",
            "phone": "+79955553535",
        }
        self.client.post(
            reverse("custom_auth:register"),
            data=data
        )
        user = self.User.objects.get(email=data.get("email"))
        self.assertTrue(
            Profile.objects.filter(user=user).exists(),
            "Успешно был создан профиль пользователя с помощью формы CustomUserCreationForm"
        )

    @classmethod
    def tearDownClass(cls):
        """ По завершении тестов удаляем пользователя """
        cls.user.delete()

    def test_profile_login(self):
        """
        Тест логина не аутентифицированного пользователя

        1. Сначала проверяем, что пользователь не залогинен
        2. Выполняем логин пользователя
        3. Проверяем, что логин прошел успешно

        """
        response = self.client.get("/")
        self.assertFalse(
            response.context["user"].is_authenticated,
            "Пользователь в данный момент не залогинен"
        )
        self.client.login(**self.credentials)
        response = self.client.get("/")
        self.assertTrue(
            response.context["user"].is_authenticated,
            "Пользователь успешно залогинился"
        )

    def test_create_profile_with_superuser(self):
        """ Тест создания профиля суперпользователя """
        superuser = self.User.objects.create_superuser(
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

    def test_user_change_password_form_success(self):
        """
        Тест формы CustomUserChangeForm - успешная смена пароля пользователя
        """
        form = CustomUserChangeForm(
            data={
                "email": self.user.email,
                "password": self.user.password,
                "new_password1": "new_admin_password",
                "new_password2": "new_admin_password",
            }
        )
        form.is_valid()
        self.assertEqual(
            form.cleaned_data.get("new_password1"),
            form.cleaned_data.get("new_password2"),
            "Успешно изменили пароль на новый в форме CustomUserChangeForm"
        )

    def test_user_change_password_form_fail(self):
        """
        Тест формы CustomUserChangeForm - неуспешная смена пароля пользователя
        """
        form = CustomUserChangeForm(
            data={
                "email": self.user.email,
                "password": self.user.password,
                "new_password1": "old_admin_password",
                "new_password2": "new_admin_password",
            }
        )
        form.is_valid()
        self.assertNotEqual(
            form.cleaned_data.get("new_password1"),
            form.cleaned_data.get("new_password2"),
            "При смене не совпали указанные пароли в форме CustomUserChangeForm"
        )
