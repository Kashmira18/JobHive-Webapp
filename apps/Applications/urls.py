from django.urls import path
from . import views
app_name = "applications" 
urlpatterns = [
    # path("my-applications/", views.my_applications, name="my_applications"),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('success/<int:app_id>/', views.application_success, name='application_success'),

]