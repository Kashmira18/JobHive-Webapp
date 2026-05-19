from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('base/', views.base, name='base'),
]