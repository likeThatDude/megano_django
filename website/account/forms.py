from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser, Profile


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2"]


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class ProfileChangeForm(forms.ModelForm):
    """
    Форма для редактирования профиля (поля профиля + поля пользователя)

    email - почта пользователя
    first_name - имя в профиле
    last_name - фамилия в профиле
    patronymic - отчество в профиле (необязательно)
    phone - номер телефона профиля
    photo - фотография профиля
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "patronymic", 'phone', 'photo']
