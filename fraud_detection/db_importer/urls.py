from django.urls import path
from . import views

urlpatterns = [

    path('', views.import_csv_to_db, name='import_csv_to_db'),
    path('success/', views.success_page, name='success_page'),
]
