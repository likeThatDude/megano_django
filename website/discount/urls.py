from django.urls import path

from .views import ActiveDiscountsView
from .views import DiscountCreateView
from .views import DiscountDetailView
from .views import DiscountListView
from .views import DiscountUpdateView

app_name = "discount"

urlpatterns = [
    path("", DiscountListView.as_view(), name="discounts"),
    path("create/", DiscountCreateView.as_view(), name="discount-create"),
    path("detail/<str:slug>/", DiscountDetailView.as_view(), name="discount-detail"),
    path("update/<str:slug>/", DiscountUpdateView.as_view(), name="discount-update"),
    path("active_discounts/", ActiveDiscountsView.as_view(), name="active_discounts"),
]
