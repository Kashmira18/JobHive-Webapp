import profile

from django.shortcuts import render

from accounts.models import CompanyProfile

# Create your views here.

# from .decorators import candidate_login_required


# @candidate_login_required
# def company_dashboard(request):
#     return render(request, "company/company_dashboard.html")


def base(request):
    return render(request, "company/company_base.html")



# ════════════════════════════════
#  DASHBOARD — Main Page
# ════════════════════════════════
# @company_required
def company_dashboard(request):
    # profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    return render(request, 'company/company_dashboard.html', {'profile': profile})


# ════════════════════════════════
#  ACTIVE JOBS
# ════════════════════════════════
# @company_required
def company_active_jobs(request):
    return render(request, "company/company_active_jobs.html")


# ════════════════════════════════
#  DRAFT JOBS
# ════════════════════════════════
# @company_required
def company_draft_jobs(request):
    return render(request, "company/company_drafts_jobs.html")


# ════════════════════════════════
#  JOB LIST
# ════════════════════════════════
# @company_required
def company_job_list(request):
    return render(request, "company/company_job_list.html")


# ════════════════════════════════
#  POST A JOB
# ════════════════════════════════
# @company_required
def company_job_post(request):
    return render(request, "company/company_job_post.html")


# ════════════════════════════════
#  MESSENGER
# ════════════════════════════════
# @company_required
def company_messenger(request):
    return render(request, "company/company_messenger.html")


# ════════════════════════════════
#  MY PROFILE
# ════════════════════════════════
# @company_required
def company_my_profile(request):
    # profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    return render(request, "company/company_my_profile.html", {"profile": profile})


# ════════════════════════════════
#  ACCOUNT SETTINGS
# ════════════════════════════════
# @company_required
def company_account_settings(request):
    return render(request, "company/company_account_setting.html")
