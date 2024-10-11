from django.urls import path

from .views import about_view, index

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("about/", about_view, name="about"),
]
