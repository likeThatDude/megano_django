from django.urls import path

from .views import AddProductInCart
from .views import DeleteProductInCart
from .views import DetailCart
from .views import GetTotalPriceCart
from .views import GetTotalQuantityCart
from .views import UpdateQuantityProductInCart
from .views import GetCostProductInCart

app_name = "cart"

urlpatterns = [
    path("detail/", DetailCart.as_view(), name="detail"),
    path("update/", UpdateQuantityProductInCart.as_view(), name="update_product"),
    path("total_quantity/", GetTotalQuantityCart.as_view(), name="total_quantity"),
    path("total_price/", GetTotalPriceCart.as_view(), name="total_price"),
    path("delete/<str:product_id>/", DeleteProductInCart.as_view(), name="delete_product"),
    path("get_cost/<str:product_id>/<int:quantity>/", GetCostProductInCart.as_view(), name="get_cost_product"),
    path("get_cost/<str:product_id>/", GetCostProductInCart.as_view(), name="get_cost_product"),
    path(
        "add_product/<str:product_id>/<str:price_id>/",
        AddProductInCart.as_view(),
        name="add_product",
    ),
]
