from django.urls import path

from .views import AddProductInCart
from .views import DeleteProductInCart
from .views import DetailCart
from .views import GetTotalPriceCart
from .views import GetTotalQuantityCart
from .views import UpdateQuantityProductInCart

app_name = "cart"

urlpatterns = [
    path("detail/", DetailCart.as_view(), name="detail"),
    path("update/", UpdateQuantityProductInCart.as_view(), name="update_product"),
    path("total_quantity/", GetTotalQuantityCart.as_view(), name="total_quantity"),
    path("total_price/", GetTotalPriceCart.as_view(), name="total_price"),
    path("delete/<int:product_id>/", DeleteProductInCart.as_view(), name="delete_product"),
    path(
        "add_product/<int:product_id>/<int:price_id>/",
        AddProductInCart.as_view(),
        name="add_product",
    ),
]
