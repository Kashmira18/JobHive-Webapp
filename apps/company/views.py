import profile

from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import CompanyProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from job.models import JobPost
from .forms import JobPostForm
from custom_admin.decorators import admin_login_required
from .decorators import approved_company_required
from applications.models import Applications
# Create your views here.

# from .decorators import candidate_login_required


# @candidate_login_required
# def company_dashboard(request):
#     return render(request, "company/company_dashboard.html")

def publish_job_view(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    
    job.is_draft = False  # Ya jo bhi aapne field rakhi hai (e.g., status="PUBLISHED")
    job.save()
    
    return redirect('company:company_active_jobs')


def base(request):
    return render(request, "company/company_base.html")


# ════════════════════════════════
#  DASHBOARD — Main Page
# ════════════════════════════════
# @company_required
# @login_required
# @approved_company_required
@login_required(login_url='login')
def company_dashboard(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    jobs = JobPost.objects.filter(company=profile)
    # applications
    applications = Applications.objects.filter(
        job__company=profile
    ).select_related('candidate__user', 'job').order_by('-applied_at')
    
    total_jobs = jobs.count()
    live_jobs = jobs.filter(status="PUBLISHED").count()
    pending_jobs = jobs.filter(status="PENDING_REVIEW").count()
    total_applied = applications.count()
    return render(request, 'company/company_dashboard.html', {
        'profile': profile,
        'total_jobs': total_jobs,
        'live_jobs': live_jobs,
        'pending_jobs': pending_jobs,
        'total_applied': total_applied,                   
        'recent_applicants': applications[:10],           

    })


# ════════════════════════════════
#  ACTIVE JOBS
# ════════════════════════════════
# @company_required
@login_required
def company_active_jobs(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    jobs = JobPost.objects.filter(company=profile, status="PUBLISHED")
    return render(request, "company/company_active_jobs.html", {
        "jobs": jobs,
        "profile": profile,
    })

 
# ════════════════════════════════
#  DRAFT JOBS
# ════════════════════════════════
# @company_required
@login_required
def company_draft_jobs(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    jobs = JobPost.objects.filter(company=profile, status="DRAFT")
    return render(request, "company/company_drafts_jobs.html", {
        "jobs": jobs,
        "profile": profile,
    })


# ════════════════════════════════
#  JOB LIST
# ════════════════════════════════
# @company_required
@login_required
def company_job_list(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    jobs = JobPost.objects.filter(company=profile)
    return render(request, "company/company_job_list.html", {
        "jobs": jobs,
        "profile": profile,
    })

def company_job_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    return render(request, "company/company_job_detail.html", {"job": job})


# ════════════════════════════════
#  POST A JOB
# ════════════════════════════════
# @company_required
# @login_required
# def company_job_post(request):
#     return render(request, "company/company_job_post.html")


# ════════════════════════════════
#  MESSENGER
# ════════════════════════════════
# @company_required
@login_required
def company_messenger(request):
    return render(request, "company/company_messenger.html")


# ════════════════════════════════
#  MY PROFILE
# ════════════════════════════════
# @company_required
@login_required
def company_my_profile(request):
    # profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    return render(request, "company/company_my_profile.html", {"profile": profile})


# ════════════════════════════════
#  ACCOUNT SETTINGS
# ════════════════════════════════
# @company_required
@login_required
def company_account_settings(request):
    return render(request, "company/company_account_setting.html")


# ─────────────────────────────────────────────────────────
#  CREATE JOB
# ─────────────────────────────────────────────────────────
@approved_company_required
# def create_job(request):
def company_job_post(request, job_id=None):
    """
    Multi-step job posting form.
    All 4 steps submit as a single POST to this view.
 
    Hidden fields filled by JavaScript before submission:
      - job_type     ← pickedType variable
      - skills       ← tags array joined by comma
      - perks        ← perks array joined by comma
      - description  ← contenteditable #jobDesc innerHTML
      - action       ← "publish" or "draft"
    """
    profile = request.user.company_profile

    job = None
    if job_id:
        job = get_object_or_404(JobPost, pk=job_id, company=profile)

    if request.method == "GET":
        form = JobPostForm(instance=job)
        post_data = None
        if job:
            post_data = {
                "title": job.title,
                "category": job.category,
                "experience_level": job.experience_level,
                "job_type": job.job_type,
                "location": job.location,
                "work_mode": job.work_mode,
                "deadline": job.deadline.isoformat() if job.deadline else "",
                "vacancies": job.vacancies,
                "qualifications": job.qualifications,
                "minimum_education": job.minimum_education,
                "years_of_experience": job.years_of_experience,
                "responsibilities": job.responsibilities,
                "salary_type": job.salary_type,
                "currency": job.currency,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_fixed": job.salary_fixed,
                "additional_notes": job.additional_notes,
                "visibility": job.visibility,
            }

        return render(request, "company/company_job_post.html", {
            "form": form,
            "job": job,
            "post_data": post_data,
        })

        # return render(request, "company/company_job_post.html", {"form": form, "job": job})
    

 
    # ── POST ──
    form   = JobPostForm(request.POST, instance=job)
    action = request.POST.get("action", "publish")
 
    if form.is_valid():
        job = form.save(commit=False)
 
        # Attach company profile
        job.company = profile
 
        # Set status based on action
        job.status = "PUBLISHED" if action == "publish" else "DRAFT"

        job.save()

        # ── Success response ──
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # AJAX request — return JSON
            return JsonResponse({
                "success":      True,
                "status":       job.status,
                "job_id":       job.pk,
                "redirect_url": "/company/jobs/",
            })

        # Normal form submit
        if action == "publish":
            messages.success(request, f'"{job.title}" submitted for review. It will go live within 24 hours.')
        else:
            messages.success(request, f'"{job.title}" saved as draft.')

        return redirect("company:company_job_list")

    # ── Form invalid — re-render with errors ──
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": False,
            "errors":  form.errors,
        }, status=400)

    # Collect error messages for template toast
    for field, errs in form.errors.items():
        for err in errs:
            messages.error(request, f"{field}: {err}")

    return render(request, "company/company_job_post.html", {
    "form": form,
    "job": job,
    "post_data": request.POST,
})


# ─────────────────────────────────────────────────────────
#  MANAGE JOBS (company's own job list)
# ─────────────────────────────────────────────────────────
@approved_company_required
def manage_jobs(request):
    """
    List all jobs posted by the logged-in company.
    Supports status filter via ?status=PUBLISHED etc.
    """
    profile     = request.user.company_profile
    status_filter = request.GET.get("status", "")

    jobs = JobPost.objects.filter(company=profile)

    if status_filter:
        jobs = jobs.filter(status=status_filter)

    # Stats
    stats = {
        "total":          jobs.count(),
        "published":      JobPost.objects.filter(company=profile, status="PUBLISHED").count(),
        "pending_review": JobPost.objects.filter(company=profile, status="PENDING_REVIEW").count(),
        "draft":          JobPost.objects.filter(company=profile, status="DRAFT").count(),
        "closed":         JobPost.objects.filter(company=profile, status="CLOSED").count(),
    }

    return render(request, "company/company_job_list.html", {
        "jobs":          jobs,
        "stats":         stats,
        "status_filter": status_filter,
        "profile":       profile,
    })


# ─────────────────────────────────────────────────────────
#  CLOSE / DELETE JOB
# ─────────────────────────────────────────────────────────
@approved_company_required
def close_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    job.status = "CLOSED"
    job.save()
    messages.success(request, f'"{job.title}" has been closed.')
    return redirect("company:company_job_list")


@approved_company_required
def delete_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    title   = job.title
    job.delete()
    messages.success(request, f'"{title}" has been deleted.')
    return redirect("company:company_job_list")


@approved_company_required
def publish_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    job.status = "PUBLISHED"
    job.save()
    messages.success(request, f'"{job.title}" has been published successfully.')
    return redirect("company:company_job_list")

# @login_required
def job_applications(request, job_id):

    job = get_object_or_404(
        JobPost,
        id=job_id,
        company=request.user.company_profile
    )

    applications = job.applications.select_related(
        "candidate"
    )

    return render(
        request,
        "company/job_applications.html",
        {
            "job": job,
            "applications": applications
        }
    )