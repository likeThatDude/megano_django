from django.urls import path

from .views import (DiscountCreateView,
                    ActiveDiscountsView,
                    DiscountUpdateView,
                    )


app_name = "discount"

urlpatterns = [
    path("create/", DiscountCreateView.as_view(), name="discount-create"),
    path("update/<str:slug>/", DiscountUpdateView.as_view(), name="discount-update"),
    path('active_discounts/', ActiveDiscountsView.as_view(), name='active_discounts'),
]
