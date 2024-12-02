from django.urls import path

from .views import DiscountCreateView
from .views import DiscountUpdateView, DiscountDetailView

app_name = "discount"

urlpatterns = [
    path("create/", DiscountCreateView.as_view(), name="discount-create"),
    path("detail/<str:slug>/", DiscountDetailView.as_view(), name="discount-detail"),
    path("update/<str:slug>/", DiscountUpdateView.as_view(), name="discount-update"),
]
