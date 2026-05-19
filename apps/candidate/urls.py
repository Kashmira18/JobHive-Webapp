from django.urls import path
from . import views

app_name = 'candidate'

urlpatterns = [
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    # path('profile/', views.profile, name='profile'),
    # Aur URLs add karo
]