from django.urls import path


from .views import (about_view, index,
                    catalog, comparison,
                    account, cart,
                    login, registr)

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("about/", about_view, name="about"),
    path("catalog/", catalog, name="catalog"),
    path("comparison/", comparison, name="comparison"),
    path("account/", account, name="account"),
    path("cart/", cart, name="cart"),
    path("login/", login, name="login"),
    path("registr", registr, name="registr")
]