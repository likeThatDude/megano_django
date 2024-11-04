from django.urls import path

from .views import ViewedListActionsView, ViewedListView, ViewsCountView

app_name = "viewed"

urlpatterns = [
    path("views", ViewedListView.as_view(), name="views-list"),
    path(
        "views/<int:product_id>", ViewedListActionsView.as_view(), name="views-actions"
    ),
    path("views/<int:product_id>/count", ViewsCountView.as_view(), name="views-count"),
]
