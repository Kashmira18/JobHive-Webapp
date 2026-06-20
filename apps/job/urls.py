# from django.urls import path
# from . import views
# from company import views as company_views
# app_name = "job"

# urlpatterns = [
    # Public job listings (candidates see these)
    # path("",           views.job_list,   name="job_list"),
    # path("<int:pk>/",  views.job_detail, name="job_detail"),
# ]


# app_name = "company"

# urlpatterns = [
#     # Dashboard
#     # path("dashboard/",                      views.company_dashboard, name="company_dashboard"),
#     path("dashboard/", company_views.company_dashboard, name="company_dashboard"),

#     # Job management
#     path("job/",                           company_views.manage_jobs,       name="manage_jobs"),
#     path("job/post/",                      company_views.company_job_post,        name="post_job"),
#     path("job/<int:job_id>/close/",        company_views.close_job,         name="close_job"),
#     path("job/<int:job_id>/delete/",       company_views.delete_job,        name="delete_job"),
# ]



from django.urls import path
from . import views

app_name = "job"

urlpatterns = [
    # Public job listings (candidates see these)
    path("",           views.job_list,   name="job_list"),
    # path("", views.company_dashboard, name="company_dashboard"),
    path("<int:pk>/",  views.job_detail, name="job_detail"),
]



