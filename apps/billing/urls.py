from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('checkout/', views.initiate_payment, name='initiate_payment'),
]