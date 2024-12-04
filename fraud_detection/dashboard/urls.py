from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard/index'),
    path('manage_models/', views.manage_models, name='dashboard/manage_models'),
    path('train_model_result', views.train_model_result, name='dashboard/train_model_result')
]

# Htmx related urls
urlpatterns += [
    path('train_model_form', views.train_model_form, name='train_model_form'),
    path('dismiss_model_form', views.cancel_model_form, name='cancel_model_form')
]