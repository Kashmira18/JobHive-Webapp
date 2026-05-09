from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name ='logout'),

    path('forget-password/', views.custom_forget_password, name='forget_password'),
    path('reset-confirm/<uidb64>/<token>', views.custom_password_reset_confirm, name='reset-password')
]