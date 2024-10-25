from django.urls import path

from .views import AddProductInCart, DetailCart

app_name = 'cart'

urlpatterns = [
    path("detail/", DetailCart.as_view(), name='detail'),
    path("add_product/<int:product_id>/<int:seller_id>/", AddProductInCart.as_view(), name='add_product'),
]
