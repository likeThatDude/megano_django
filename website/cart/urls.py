from django.urls import path

from .views import APICart
from .views import DetailCart

app_name = "cart"

urlpatterns = [
    path("detail/", DetailCart.as_view(), name="detail"),
    path("api/", APICart.as_view(), name="api"),
]
