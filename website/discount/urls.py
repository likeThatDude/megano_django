from django.urls import path

from .views import DiscountCreateView
from .views import DiscountUpdateView, DiscountDetailView, DiscountListView

app_name = "discount"

urlpatterns = [
    path("", DiscountListView.as_view(), name="discounts"),
    path("create/", DiscountCreateView.as_view(), name="discount-create"),
    path("detail/<str:slug>/", DiscountDetailView.as_view(), name="discount-detail"),
    path("update/<str:slug>/", DiscountUpdateView.as_view(), name="discount-update"),
]
