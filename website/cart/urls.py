from django.urls import path

from .views import DetailCart, AddProductInCart, DeleteProductInCart, UpdateQuantityProductInCart

app_name = 'cart'

urlpatterns = [
    path("detail/", DetailCart.as_view(), name='detail'),
    path("add_product/<int:product_id>/<int:price_id>/", AddProductInCart.as_view(), name='add_product'),
    path("update/<int:product_id>/<int:price_id>/", UpdateQuantityProductInCart.as_view(), name='update_product'),
    path("delete/<int:product_id>/", DeleteProductInCart.as_view(), name='delete_product'),
]
