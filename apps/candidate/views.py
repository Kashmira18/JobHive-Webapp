from django.shortcuts import render
# from .decorators import candidate_login_required



# @candidate_login_required
def candidate_dashboard(request):
    return render(request, 'candidate/candidate_dashboard.html')


# @candidate_login_required
# def profile(request):
#     return render(request, 'candidate/profile.html')
# CANDIDATE DASHBOARD VIEWS_______________________
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