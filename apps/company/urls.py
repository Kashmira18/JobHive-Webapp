from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('base/', views.base, name='base'),
    # path('profile/', views.company_profile, name='company_profile'),
    # # path('profile/edit/', views.edit_company_profile, name='edit_company_profile'),
    # path('job-postings/', views.job_postings, name='job_postings'),
    # # path('job-postings/create/', views.create_job_posting, name='create_job_posting'),
    # # path('job-postings/<int:pk>/edit/', views.edit_job_posting, name='edit_job_posting'),
    # # path('job-postings/<int:pk>/delete/', views.delete_job_posting, name='delete_job_posting'),
    # path('settings/', views.account_settings, name='account_settings'),
    # path('activate/', views.activate_job_posting, name='activate_job_posting'),
    # # path('deactivate/', views.deactivate_job_posting, name='deactivate_job_posting'),
    # path('drafts/', views.drafts, name='drafts'),


    path('company/active-jobs/',    views.company_active_jobs,     name='company_active_jobs'),
    path('company/draft-jobs/',     views.company_draft_jobs,      name='company_draft_jobs'),
    # path('company/job-list/',       views.company_job_list,        name='company_job_list'),
    # path('company/job-post/',       views.company_job_post,        name='company_job_post'),
    path('job-list/', views.company_job_list, name='company_job_list'),
    path('job-post/', views.company_job_post, name='company_job_post'),

    path('company/messenger/',      views.company_messenger,       name='company_messenger'),
    path('company/profile/',        views.company_my_profile,      name='company_my_profile'),
    path('company/settings/',       views.company_account_settings, name='company_account_settings'),
    path('company/job/<int:job_id>/publish/', views.publish_job_view, name='publish_job'),


    
    # Job management
    path("job/",                           views.manage_jobs,       name="manage_jobs"),
    path("job/post/",                      views.company_job_post,        name="post_job"),
    path("job/<int:job_id>/close/",        views.close_job,         name="close_job"),
    path("job/<int:job_id>/delete/",       views.delete_job,        name="delete_job"),
    # Job detail (View)
    path('job/<int:pk>/', views.company_job_detail, name='company_job_detail'),
    

    # Job edit
    path('job-post/<int:job_id>/edit/', views.company_job_post, name='company_job_edit'),
    

]