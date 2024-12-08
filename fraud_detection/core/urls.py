from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='core/index'),
    path('register/', views.get_register_form, name='core/register'),
    path('post_register/', views.post_register_form, name='core/post_register'),
    path('logout/', views.logout_view, name='core/logout'),
    path('login/', views.login_view, name='core/login'),
    path('post_login/', views.post_login_view, name='core/post_login'),
    path('profile/', views.profile_view, name='core/profile'),
    path('update_profile/', views.update_profile_view, name='core/update_profile'),
    path('change_password/', views.get_change_password_view, name='core/change_password'),
    path('post_change_password/', views.post_change_password_view, name='core/post_change_password'),
    path('detection_page/', views.detection_page_view, name='core/detection_page'),
]
