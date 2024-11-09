from catalog.models import Delivery
from catalog.models import Payment
from django import forms
from django.core.exceptions import ValidationError
from django.http import QueryDict


class OrderForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True)
    mail = forms.EmailField(required=True)
    choice_delivery_type = forms.CharField(max_length=15, required=True)
    city = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=100, required=True)

    def clean_choice_delivery_type(self):
        delivery_type = self.cleaned_data.get("choice_delivery_type")
        if delivery_type not in ["store", "seller"]:
            raise ValidationError("Неверный тип данных для доставки")
        return delivery_type

    def clean(self):
        post_data: QueryDict = self.data
        keys_data: list[str] = [key for key, value in post_data.items()]

        cleaned_data: dict[str, str] = super().clean()
        self.check_delivery_type(keys_data, post_data, cleaned_data)
        self.check_payment_method(keys_data, post_data, cleaned_data)

        return cleaned_data

    @staticmethod
    def check_delivery_type(keys_data: list[str], post_data: QueryDict, cleaned_data: dict[str, str]) -> None:
        delivery_choices: list[str] = list(dict(Delivery.DELIVERY_CHOICES).keys())

        if "delivery_" not in keys_data and "delivery" not in keys_data:
            raise ValidationError("Не найдены данные о способе доставки")

        for key, value in post_data.items():
            if key.startswith("delivery"):
                if value not in delivery_choices:
                    raise forms.ValidationError(f"Неверный тип данных для {key}")
                cleaned_data[key] = value

    @staticmethod
    def check_payment_method(keys_data: list[str], post_data: QueryDict, cleaned_data: dict[str, str]) -> None:
        payments_choices: list[str] = list(dict(Payment.PAYMENT_CHOICES).keys())

        if "pay" not in keys_data and "pay_" not in keys_data:
            raise ValidationError("Не найдены данные о способе оплаты")

        for key, value in post_data.items():
            if key.startswith("pay"):
                if value not in payments_choices:
                    raise forms.ValidationError(f"Неверный тип данных для поля {key}")
                cleaned_data[key] = value
