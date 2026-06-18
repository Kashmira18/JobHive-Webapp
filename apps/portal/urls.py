from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),
    path("navbar/", views.navbar, name="navbar"),
    path("navbar2/", views.navbar2, name="navbar2"),
    path("find_jobs/", views.find_jobs, name="find_jobs"),
    path("job_list/", views.job_list, name="job_list"),
    path("job_details/", views.job_details, name="job_details"),
    # path("employers/", views.employers, name="employers"),
    # path("candidates/", views.candidates, name="candidates"),
    path("blog/", views.blog, name="blog"),
    path("blog_detail/", views.blog_detail, name="blog_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("candidates/", views.candidates, name="candidates"),
    # path("candidates-detail/", views.candidatesdetail, name="candidates-detail"),
    # path("candidates-list/", views.candidateslist, name="candidates-list"),
    # path("Company-list/", views.Companylist, name="Company-list"),
    # path("company-detail/", views.companydetail, name="company-detail"),
    path("footer/", views.footer, name="footer"),
    path("error_404/", views.error_404, name="error_404"),
    # path("post_job/", views.post_job, name="post_job"),
    

]

