from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='index'),
    path('register/', views.get_register_form, name='register'),
    path('users/', views.post_register_form, name='users'),
]
