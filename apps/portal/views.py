# from django.shortcuts import render
from django.shortcuts import render, redirect
# Create your views here.

def home(request):
    return render(request, "portal/home.html")

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


