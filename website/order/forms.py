import bleach
from catalog.models import Delivery
from catalog.models import Payment
from django import forms
from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _


class OrderForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": _("The name is a required field to fill in."),
            "max_length": _("The name cannot be longer than 100 characters."),
        },
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            "required": _("Phone number is a required field to fill in."),
            "max_length": _("The phone number cannot be longer than 15 characters."),
        },
    )
    mail = forms.EmailField(
        required=True,
        error_messages={
            "required": _("Email is a required field to fill in."),
            "invalid": _("Enter the correct email address."),
        },
    )
    choice_delivery_type = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            "required": _("The type of delivery is a required field to fill in."),
            "max_length": _("The delivery type cannot be longer than 15 characters."),
        },
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": _("The city is a required field to fill in."),
            "max_length": _("The name of the city cannot be longer than 100 characters."),
        },
    )
    address = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": _("The address is a required field to fill in."),
            "max_length": _("The address cannot be longer than 100 characters."),
        },
    )
    comment = forms.CharField(
        max_length=1000,
        required=False,
        error_messages={
            "max_length": _("The comment cannot be longer than 1000 characters."),
        },
    )

    def clean_choice_delivery_type(self):
        delivery_type = self.cleaned_data.get("choice_delivery_type")
        cleaned_delivery_type = bleach.clean(delivery_type, tags=[], strip=True)
        if cleaned_delivery_type not in ["store", "seller"]:
            raise ValidationError(_("Delivery method: Invalid data type for delivery"))
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
            raise ValidationError(_("No information about the delivery method was found"))

        for key, value in post_data.items():
            if key.startswith("delivery"):
                if value not in delivery_choices:
                    raise forms.ValidationError(_(f"Invalid data type for {key}"))
                cleaned_data[key] = value

    @staticmethod
    def check_payment_method(keys_data: list[str], post_data: QueryDict, cleaned_data: dict[str, str]) -> None:
        payments_choices: list[str] = list(dict(Payment.PAYMENT_CHOICES).keys())

        if "pay" not in keys_data and "pay_" not in keys_data:
            raise ValidationError(_("No information about the payment method was found"))

        for key, value in post_data.items():
            if key.startswith("pay"):
                if value not in payments_choices:
                    raise forms.ValidationError(_(f"Invalid data type for the field {key}"))
                cleaned_data[key] = value
