from django.urls import path
from core.views import index
from core.imports.views import import_products_view

# from .views import (about_view, index,
#                     catalog, comparison,
#                     account, cart,
#                     login, registr)

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path('import/', import_products_view, name='import_products'),
    # path("about/", about_view, name="about"),
    # path("catalog/", catalog, name="catalog"),
    # path("comparison/", comparison, name="comparison"),
    # path("account/", account, name="account"),
    # path("cart/", cart, name="cart"),
]
