from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name ='logout'),

    path('forget-password/', views.custom_forget_password, name='forget_password'),
    path('reset-password/done/', views.custom_password_reset_done, name='password_reset_done'),
    # path('reset-password/<str:uidb64>/<str:token>/', views.custom_password_reset_confirm, name='password_reset_confirm'),
    # path('reset-confirm/<uidb64>/<token>', views.custom_password_reset_confirm, name='reset-password'),
    path('reset-password/<str:uidb64>/<str:token>/',      views.custom_password_reset_confirm,   name='password_reset_confirm'),
    path('reset-password/invalid/', views.custom_password_reset_invalid, name='password_reset_invalid'),
    

]