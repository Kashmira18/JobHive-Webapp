from django.shortcuts import render
from job.models import JobPost
# from .decorators import candidate_login_required


# @candidate_login_required
def candidate_dashboard(request):
    featured_jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company").order_by("-created_at")[:6]
    return render(request, 'candidate/candidate_dashboard.html', {
        "featured_jobs": featured_jobs,
    })


# @candidate_login_required
# def profile(request):
#     return render(request, 'candidate/profile.html')
# CANDIDATE DASHBOARD
def candidate_base(request):
    return render(request, "candidate/candidate_base.html")
def candidate_edit_profile(request):
    return render(request,"candidate/candidate_edit_profile.html")
def bookmark_jobs(request):
    return render(request,"candidate/Bookmark_Jobs.html")
def applied_jobs(request):
    return render(request,"candidate/applied_jobs.html")
def candidate_edit_resume(request):
    return render(request,"candidate/edit_resume.html")
def job_alert(request):
    return render(request,"candidate/job_alert.html")
def candidate_notifications(request):
    return render(request,"candidate/notifications.html")
def candidate_view_resume(request):
    return render(request,"candidate/viewresume.html")
def candidate_setting(request):
    return render(request, "candidate/candidate_setting.html")
def messenger(request):
    return render(request, 'candidate/messenger.html')