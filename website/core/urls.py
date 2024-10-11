from django.urls import path
from . import views

from .views import about_view, index, catalog

app_name = "core"

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("", index, name="index"),
    path("about/", about_view, name="about"),
    path("catalog/", catalog, name="catalog")
]
