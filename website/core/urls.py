from django.urls import path

from .views import index, about_view

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("about/", about_view, name="about"),
]
