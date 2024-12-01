from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard/index'),
    path('manage_models/', views.manage_models, name='dashboard/manage_models')
]
