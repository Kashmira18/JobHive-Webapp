# from django.shortcuts import render
from django.shortcuts import render, redirect
from job.models import JobPost
# Create your views here.

def home(request):
    published_jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company").order_by("-created_at")
    total_jobs = published_jobs.count()
    recent_jobs = published_jobs[:6]   # up to 6 for the "Recent Job Circulars" section
    trending_jobs = published_jobs[:3]  # up to 3 for the trending bar
    return render(request, "portal/home.html", {
        "published_jobs": published_jobs,
        "recent_jobs": recent_jobs,
        "trending_jobs": trending_jobs,
        "total_jobs": total_jobs,
    })

def selector(request):
    return render(request, "portal/selector.html")

def navbar(request):
    return render(request, "portal/navbar.html")

def navbar2(request):
    return render(request, "portal/navbar2.html")

def footer(request):
    return render(request, "portal/footer.html")

def about(request):
    return render(request, "portal/about.html")

def find_jobs(request):
    return render(request, "portal/find_jobs.html")
# ____________
def job_list(request):
    return render(request, "portal/job_list.html")

def job_details(request):
    return render(request, "portal/job_details.html")

def blog(request):
    return render(request, "portal/blog.html")

def blog_detail(request):
    return render(request, "portal/blog_detail.html")

def candidates(request):
    return render(request, "portal/candidates.html")

def contact(request):
    return render(request, "portal/contact.html")

def error_404(request):
    return render(request, "portal/error_404.html")


