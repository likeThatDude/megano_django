from django import forms
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .models import Discount, ProductGroup
from catalog.models import Category, Product


class DiscountCreationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Название к скидке, например, \"Распродажа 11.11.\""),
            },
        ),
        error_messages={
            "max_length": _("Допустимо только 100 символов"),
        },
        label=_("Название скидки"),
    )
    kind = forms.ChoiceField(
        required=True,
        choices=Discount.KIND_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
        error_messages={
            "required": _("Заполните обязательное поле"),
        },
        label=_("Тип скидки"),
    )
    method = forms.ChoiceField(
        required=True,
        choices=Discount.METHOD_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
        error_messages={
            "required": _("Заполните обязательное поле"),
        },
        label=_("Механизм скидки"),
    )
    quantity_gt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Максимальное количество"),
            },
        ),
        label=_("Максимальное количество"),
    )
    quantity_lt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Минимальное количество")
            },
        ),
        label=_("Минимальное количество"),
    )
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Введите значение скидки")
            },
        ),
        label=_("Значение скидки"),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": _("Описание скидки..."), "rows": 3},
        ),
        label=_("Описание"),
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"},
        ),
        label=_("Дата начала действия скидки"),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"},
        ),
        label=_("Дата окончания действия скидки"),
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"},
        ),
        label=_("Активно"),
    )
    archived = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"},
        ),
        label=_("Архивировано"),
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Выберите товары, к которым применить скидку"),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Выберите категории товаров, в которым применить скидку"),
    )
    products_group = forms.ModelMultipleChoiceField(
        queryset=ProductGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Выберите группу товаров, к которой применим скидку"),
    )

    class Meta:
        model = Discount
        fields = [
            "name",
            "kind",
            "method",
            "quantity_gt",
            "quantity_lt",
            "value",
            "description",
            "start_date",
            "end_date",
            "is_active",
            "archived",
            "products",
            "categories",
            "product_groups",
        ]

    def __init__(self, *args, **kwargs):
        """
        Устанавливаем атрибут value к полям start_date и end_date со значением
        текущей даты
        """
        super().__init__(*args, **kwargs)
        self.fields['end_date'].widget.attrs['value'] = now().date()
        self.fields['start_date'].widget.attrs['value'] = now().date()
