from django.urls import path
from . import views

app_name = 'candidate'

urlpatterns = [
    path("candidate_base/", views.candidate_base, name="candidate_base"),
    path("candidate_dashboard/", views.candidate_dashboard, name="candidate_dashboard"),
    path("profile/", views.candidate_edit_profile, name="candidate_edit_profile"),

    # Save endpoints
    path('profile/save/personal/',      views.save_personal_info,    name='save_personal_info'),
    path('profile/save/professional/',  views.save_professional_info, name='save_professional_info'),
    path('profile/save/location/',      views.save_location,          name='save_location'),
    path('profile/save/about/',         views.save_about_me,          name='save_about_me'),
    path('profile/save/resume/',        views.save_resume,            name='save_resume'),
    path('profile/save/skills/',        views.save_skills,            name='save_skills'),
    path('profile/save/education/',     views.save_education,         name='save_education'),
    path('profile/save/experience/',    views.save_experience,        name='save_experience'),
    path('profile/save/social/',        views.save_social_links,      name='save_social_links'),
    path("bookmark_jobs/", views.bookmark_jobs, name="bookmark_jobs"),
    path("applied_jobs/", views.applied_jobs, name="applied_jobs"),
    path("candidate_edit_resume/", views.candidate_edit_resume, name="candidate_edit_resume"),
    path("job_alert/", views.job_alert, name="job_alert"),
    path("candidate_notifications/", views.candidate_notifications, name="candidate_notifications"),
    path("candidate_view_resume/", views.candidate_view_resume, name="candidate_view_resume"),
    path("setting/", views.candidate_setting, name="candidate_setting"),
    path('messenger/', views.messenger, name="messenger"),

    
]
