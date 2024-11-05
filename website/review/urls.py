from django.urls import path

from . import views

app_name = "review"

urlpatterns = [
    path("review/<int:product_id>/", views.ReviewListSet.as_view(), name="get_product_reviews"),
    path("review/create/", views.ReviewCreateView.as_view(), name="review_create"),
    path("review/<int:pk>/update/", views.ReviewUpdateViewSet.as_view(), name="review_update"),
    path("review/<int:pk>/delete/", views.ReviewDeleteViewSet.as_view(), name="review_delete"),
]
