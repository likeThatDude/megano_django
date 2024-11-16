from django.urls import path

from . import views
from .views import CatalogListView
from .views import ViewedListActionsView
from .views import ViewedListView
from .views import ViewsCountView

app_name = "catalog"

urlpatterns = [
    path("assortment", views.catalog_view, name="catalog"),
    path("<int:pk>", CatalogListView.as_view(), name="catalog"),
    # products
    path("products/<int:pk>", views.ProductDetailView.as_view(), name="product_detail"),
    # viewed products
    path("views", ViewedListView.as_view(), name="views-list"),
    path("views/<int:product_id>", ViewedListActionsView.as_view(), name="views-actions"),
    path("views/<int:product_id>/count", ViewsCountView.as_view(), name="views-count"),
]
