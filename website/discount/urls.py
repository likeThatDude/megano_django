from django.urls import path

from .views import DiscountCreateView

app_name = "discount"

urlpatterns = [
    path("create/", DiscountCreateView.as_view(), name="discount-create"),
]
