from django.urls import path

from . import views

app_name = "comparison"

urlpatterns = [
    path("", views.ComparisonView.as_view(), name="comparison_page"),
    path("add/", views.ComparisonAddApiView.as_view(), name="comparison_add"),
    path("delete/", views.ComparisonDeleteApiView.as_view(), name="comparison_delete"),
]
