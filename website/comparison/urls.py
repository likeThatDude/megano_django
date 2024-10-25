from django.urls import path

from . import views

app_name = "comparison"

urlpatterns = [
    path("", views.ComparisonView.as_view(), name="comparison_page"),
    path('comparison/', views.ComparisonAddView.as_view(), name="comparison_add"),
    path('delete/<int:pk>/', views.ComparisonDeleteView.as_view(), name="comparison_delete"),
]
