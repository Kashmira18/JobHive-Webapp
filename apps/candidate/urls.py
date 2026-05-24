from django.urls import path
from . import views

app_name = 'candidate'

urlpatterns = [
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    # path('profile/', views.profile, name='profile'),
    path("candidate_base/", views.candidate_base, name="candidate_base"),
    path("candidate_dashboard/", views.candidate_dashboard, name="candidate_dashboard"),
    path("candidate_edit_profile/", views.candidate_edit_profile, name="candidate_edit_profile"),
    path("bookmark_jobs/", views.bookmark_jobs, name="bookmark_jobs"),
    path("applied_jobs/", views.applied_jobs, name="applied_jobs"),
    path("candidate_edit_resume/", views.candidate_edit_resume, name="candidate_edit_resume"),
    path("job_alert/", views.job_alert, name="job_alert"),
    path("candidate_notifications/", views.candidate_notifications, name="candidate_notifications"),
    path("candidate_view_resume/", views.candidate_view_resume, name="candidate_view_resume"),
    path("setting/", views.candidate_setting, name="candidate_setting"),
    path('messenger/', views.messenger, name="messenger"),

    
]