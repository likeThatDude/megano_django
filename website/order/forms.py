from catalog.models import Delivery
from catalog.models import Payment
from django import forms
from django.core.exceptions import ValidationError
from django.http import QueryDict
import bleach
from django.utils.translation import gettext_lazy as _


class OrderForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': _('Имя это обязательное поле для заполнения.'),
            'max_length': _('Имя не может быть длиннее 100 символов.'),
        }
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            'required': _('Телефон это обязательное поле для заполнения.'),
            'max_length': _('Телефон не может быть длиннее 15 символов.'),
        }
    )
    mail = forms.EmailField(
        required=True,
        error_messages={
            'required': _('Email это обязательное поле для заполнения.'),
            'invalid': _('Введите корректный email адрес.'),
        }
    )
    choice_delivery_type = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            'required': _('Тип доставки — это обязательное поле для заполнения.'),
            'max_length': _('Тип доставки не может быть длиннее 15 символов.'),
        }
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': _('Город — это обязательное поле для заполнения.'),
            'max_length': _('Название города не может быть длиннее 100 символов.'),
        }
    )
    address = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': _('Адрес — это обязательное поле для заполнения.'),
            'max_length': _('Адрес не может быть длиннее 100 символов.'),
        }
    )
    comment = forms.CharField(
        max_length=1000,
        required=False,
        error_messages={
            'max_length': _('Комментарий не может быть длиннее 1000 символов.'),
        }
    )

    def clean_choice_delivery_type(self):
        delivery_type = self.cleaned_data.get("choice_delivery_type")
        cleaned_delivery_type = bleach.clean(delivery_type, tags=[], strip=True)
        if cleaned_delivery_type not in ["store", "seller"]:
            raise ValidationError(_("Способ доставки: Неверный тип данных для доставки"))
        return delivery_type

    def clean(self):
        post_data: QueryDict = self.data
        keys_data: list[str] = [key for key, value in post_data.items()]

        cleaned_data: dict[str, str] = super().clean()
        self.check_delivery_type(keys_data, post_data, cleaned_data)
        self.check_payment_method(keys_data, post_data, cleaned_data)

        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get("name")
        cleaned_name = bleach.clean(name, tags=[], strip=True)
        return cleaned_name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        cleaned_phone = bleach.clean(phone, tags=[], strip=True)
        return cleaned_phone

    def clean_mail(self):
        mail = self.cleaned_data.get("mail")
        cleaned_mail = bleach.clean(mail, tags=[], strip=True)
        return cleaned_mail

    def clean_city(self):
        city = self.cleaned_data.get("city")
        cleaned_city = bleach.clean(city, tags=[], strip=True)
        return cleaned_city

    def clean_address(self):
        address = self.cleaned_data.get("address")
        cleaned_address = bleach.clean(address, tags=[], strip=True)
        return cleaned_address

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        cleaned_comment = bleach.clean(comment, tags=[], strip=True)
        return cleaned_comment

    @staticmethod
    def check_delivery_type(keys_data: list[str], post_data: QueryDict, cleaned_data: dict[str, str]) -> None:
        delivery_choices: list[str] = list(dict(Delivery.DELIVERY_CHOICES).keys())

        if "delivery_" not in keys_data and "delivery" not in keys_data:
            raise ValidationError(_("Не найдены данные о способе доставки"))

        for key, value in post_data.items():
            if key.startswith("delivery"):
                if value not in delivery_choices:
                    raise forms.ValidationError(_(f"Неверный тип данных для {key}"))
                cleaned_data[key] = value

    @staticmethod
    def check_payment_method(keys_data: list[str], post_data: QueryDict, cleaned_data: dict[str, str]) -> None:
        payments_choices: list[str] = list(dict(Payment.PAYMENT_CHOICES).keys())

        if "pay" not in keys_data and "pay_" not in keys_data:
            raise ValidationError(_("Не найдены данные о способе оплаты"))

        for key, value in post_data.items():
            if key.startswith("pay"):
                if value not in payments_choices:
                    raise forms.ValidationError(_(f"Неверный тип данных для поля {key}"))
                cleaned_data[key] = value
