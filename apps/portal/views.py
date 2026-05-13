# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from functools import wraps
# from .models import JobPost, CompanyProfile
from accounts.models import CustomUser

def company_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'COMPANY':
            messages.error(request, "Access denied. Company accounts only.")
            return redirect('login')
        if not request.user.is_approved:
            messages.error(request, "Your account is pending admin approval.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── 1. Main Dashboard ──
@company_required
def company_dashboard(request):
    jobs       = JobPost.objects.filter(company=request.user)
    active     = jobs.filter(status='ACTIVE').count()
    drafts     = jobs.filter(status='DRAFT').count()
    context    = {
        'active_count': active,
        'draft_count':  drafts,
        'total_jobs':   jobs.count(),
    }
    return render(request, 'company/company_front_dashboard.html', context)


# ── 2. Job List ──
# @company_required
# def company_job_list(request):
#     jobs = JobPost.objects.filter(company=request.user)
#     return render(request, 'company/company_job_list.html', {'jobs': jobs})

# ── 3. Active Jobs ──
# @company_required
# def company_active_jobs(request):
#     jobs = JobPost.objects.filter(company=request.user, status='ACTIVE')
#     return render(request, 'company/company_active_jobs.html', {'jobs': jobs})











