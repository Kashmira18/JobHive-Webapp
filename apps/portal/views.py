# from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from job.models import JobPost
# Create your views here.

def home(request):
    published_jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company").order_by("-created_at")
    total_jobs = published_jobs.count()
    recent_jobs = published_jobs
    trending_jobs = published_jobs[:3]  # up to 3 for the trending bar
    home_categories = list(
        JobPost.objects.filter(status="PUBLISHED", visibility="public")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    return render(request, "portal/home.html", {
        "published_jobs": published_jobs,
        "recent_jobs": recent_jobs,
        "trending_jobs": trending_jobs,
        "total_jobs": total_jobs,
        "home_categories": home_categories,
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
    keyword = (request.GET.get("keyword") or "").strip()
    location = (request.GET.get("location") or "").strip()
    category = (request.GET.get("category") or "").strip()

    jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company")

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(skills__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category:
        jobs = jobs.filter(category__icontains=category)

    jobs = jobs.order_by("-created_at")

    categories = list(
        JobPost.objects.filter(status="PUBLISHED", visibility="public")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    locations = list(
        JobPost.objects.filter(status="PUBLISHED", visibility="public")
        .values_list("location", flat=True)
        .distinct()
        .order_by("location")
    )

    return render(request, "portal/job_list.html", {
        "jobs": jobs,
        "keyword": keyword,
        "location": location,
        "category": category,
        "categories": categories,
        "locations": locations,
    })

def job_details(request,job_id):
    job = get_object_or_404(JobPost, id=job_id, status="PUBLISHED")
    return render(request, "portal/job_details.html", {
        "job": job,
    })

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


