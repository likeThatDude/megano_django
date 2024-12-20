from catalog.models import Category
from catalog.models import Product
from django import forms
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .models import Discount
from .models import ProductGroup


class DiscountCreationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _('The name of the discount, for example, "Sale 11.11."'),
            },
        ),
        error_messages={
            "max_length": _("Only 100 characters are allowed"),
        },
        label=_("Name of the discount"),
    )
    kind = forms.ChoiceField(
        required=True,
        choices=Discount.KIND_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
        error_messages={
            "required": _("Fill in the required field"),
        },
        label=_("Type discount"),
    )
    method = forms.ChoiceField(
        required=True,
        choices=Discount.METHOD_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
        error_messages={
            "required": _("Fill in the required field"),
        },
        label=_("Discount method"),
    )
    quantity_gt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Maximum quantity"),
            },
        ),
        label=_("Maximum quantity"),
    )
    quantity_lt = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Minimum quantity")},
        ),
        label=_("Minimum quantity"),
    )
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Enter the discount value")},
        ),
        label=_("Discount value"),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": _("Description of the discount..."), "rows": 3},
        ),
        label=_("Description"),
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"},
        ),
        label=_("Discount start date"),
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"},
        ),
        label=_("Discount end date"),
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"},
        ),
        label=_("Active"),
    )
    archived = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"},
        ),
        label=_("Archived"),
    )
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Select the products to apply the discount to"),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Select the product categories in which to apply the discount"),
    )
    products_group = forms.ModelMultipleChoiceField(
        queryset=ProductGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input"},
        ),
        label=_("Select the product group to which the discount applies"),
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
        self.fields["end_date"].widget.attrs["value"] = now().date()
        self.fields["start_date"].widget.attrs["value"] = now().date()

    def clean_end_date(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(_("The discount expiration date cannot be earlier than the start date."))

        return end_date
