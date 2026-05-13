from django.urls import path
from . import views

urlpatterns = [
    path('company/dashboard/',          views.company_dashboard,        name='company_dashboard'),

]

