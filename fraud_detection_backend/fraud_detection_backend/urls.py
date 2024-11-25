"""
URL configuration for fraud_detection_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from detector import views as detector_views
from db_importer import views as db_importer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', detector_views.test, name='test'),
    path('api/import_data', db_importer_views.import_csv_to_db, name='import_csv_to_db'),
]
