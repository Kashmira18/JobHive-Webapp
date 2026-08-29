import profile

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.models import CompanyProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from job.models import JobPost
from .forms import JobPostForm
from custom_admin.decorators import admin_login_required
# from .decorators import approved_company_required
from applications.models import Applications
from notifications.models import Notification
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from .forms import JobPostForm, CompanyUserUpdateForm, CompanyProfileUpdateForm
from billing.models import CompanySubscription, CompanyCredit, PaymentLog, SubscriptionPlan
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
@login_required(login_url='accounts:login')
def company_dashboard(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    jobs = JobPost.objects.filter(company=profile)
    # applications
    applications = Applications.objects.filter(
        job__company=profile
    ).select_related('candidate__user', 'job').order_by('-applied_at')
    
    total_jobs = jobs.count()
    live_jobs = jobs.filter(status="PUBLISHED").count()
    total_applied = applications.count()
    return render(request, 'company/company_dashboard.html', {
        'profile': profile,
        'total_jobs': total_jobs,
        'live_jobs': live_jobs,
        'total_applied': total_applied,                   
        'recent_applicants': applications[:5],           

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
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
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
# @approved_company_required
# def create_job(request):
@login_required(login_url='accounts:login')
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
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)

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
 
        # Check if the job was already published
        was_published = False
        if job.pk:
            try:
                orig = JobPost.objects.get(pk=job.pk)
                was_published = (orig.status == "PUBLISHED")
            except JobPost.DoesNotExist:
                pass

        is_publishing = (action == "publish")

        if is_publishing and not was_published:
            credits, _ = CompanyCredit.objects.get_or_create(company=profile)
            
            try:
                subscription = profile.subscription
                limit = subscription.current_plan.job_post_limit if subscription.current_plan else 0
            except Exception:
                limit = 0
                
            published_count = JobPost.objects.filter(company=profile, status="PUBLISHED").count()
            
            if published_count < limit:
                pass # allowed via plan limit
            elif credits.available_credits > 0:
                credits.deduct_credit() # allowed via credits
            else:
                error_msg = f"You have reached your limit of {limit} jobs for your current plan. Please purchase credits or subscribe to a plan."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({
                        "success": False,
                        "errors": {"__all__": [error_msg]},
                    }, status=400)
                messages.error(request, error_msg)
                return render(request, "company/company_job_post.html", {
                    "form": form,
                    "job": job,
                    "post_data": request.POST,
                })

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
# @approved_company_required
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
# @approved_company_required
def close_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    job.status = "CLOSED"
    job.save()
    messages.success(request, f'"{job.title}" has been closed.')
    return redirect("company:company_job_list")


# @approved_company_required
def delete_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    title   = job.title
    job.delete()
    messages.success(request, f'"{title}" has been deleted.')
    return redirect("company:company_job_list")


# @approved_company_required
def publish_job(request, job_id):
    profile = request.user.company_profile
    job     = get_object_or_404(JobPost, pk=job_id, company=profile)
    
    if job.status == "PUBLISHED":
        messages.info(request, f'"{job.title}" is already published.')
        return redirect("company:company_job_list")

    try:
        subscription = profile.subscription
        limit = subscription.current_plan.job_post_limit if subscription.current_plan else 0
    except Exception:
        limit = 0
        
    published_count = JobPost.objects.filter(company=profile, status="PUBLISHED").count()
    credits, _ = CompanyCredit.objects.get_or_create(company=profile)
    
    if published_count < limit:
        pass # allowed via plan limit
    elif credits.available_credits > 0:
        credits.deduct_credit()
    else:
        messages.error(request, f"You have reached your limit of {limit} jobs for your current plan. Please purchase credits or subscribe to a plan.")
        return redirect("company:company_job_list")

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

@login_required(login_url='accounts:login')
@require_POST
def update_application_status(request):
    try:
        data = json.loads(request.body)
        app_id = data.get('application_id')
        new_status = data.get('status')
        
        profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
        application = get_object_or_404(Applications, id=app_id, job__company=profile)
        
        valid_statuses = [choice[0] for choice in Applications.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
            
        old_status = application.status
        application.status = new_status
        application.save()
        
        # Create notification for candidate
        Notification.objects.create(
            user=application.candidate.user,
            notification_type='JOB_UPDATE',
            title='Application Status Update',
            message=f'Your application for {application.job.title} at {profile.trade_name} has been updated to {application.get_status_display()}.',
            link=f'/application/success/{application.id}/' # Just a placeholder link, can be whatever the candidate dashboard is
        )
        
        return JsonResponse({'success': True, 'status': new_status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required(login_url='accounts:login')
def company_all_applicants(request):
    profile, _ = CompanyProfile.objects.get_or_create(user=request.user)
    
    applications = Applications.objects.filter(
        job__company=profile
    ).select_related('candidate__user', 'job').order_by('-applied_at')
    
    return render(request, 'company/all_applicants.html', {
        'applications': applications
    })

# ════════════════════════════════
#  ACCOUNT SETTINGS
# ════════════════════════════════
@login_required(login_url='accounts:login')
def company_account_settings(request):
    # Read active tab from query params, default to myprofile
    tab = request.GET.get('tab', 'myprofile')
    user = request.user
    
    # Get or fetch company profile safely
    company_profile, _ = CompanyProfile.objects.get_or_create(user=user)

    # Initialize forms for GET requests
    user_form = CompanyUserUpdateForm(instance=user)
    profile_form = CompanyProfileUpdateForm(instance=company_profile)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. MY PROFILE Form Handling
        if action == 'update_profile':
            user_form = CompanyUserUpdateForm(request.POST, instance=user)
            profile_form = CompanyProfileUpdateForm(request.POST, request.FILES, instance=company_profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect(f"{request.path}?tab=myprofile")
            else:
                messages.error(request, "Please correct the errors below.")
                tab = 'myprofile'

        # 2. SECURITY Form Handling
        elif action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                messages.success(request, "Your password was successfully updated!")
                return redirect(f"{request.path}?tab=security")
            else:
                messages.error(request, "Password update failed. Please check the requirements.")
                tab = 'security'

        # 3. NOTIFICATIONS Form Handling (Mock/Fallback)
        elif action == 'update_notifications':
            messages.success(request, "Notification preferences saved.")
            return redirect(f"{request.path}?tab=notifications")

        # 5. DANGER ZONE Form Handling
        elif action == 'deactivate_account':
            user.is_active = False
            user.save()
            logout(request)
            messages.info(request, "Your account has been deactivated.")
            return redirect('accounts:login')

        elif action == 'delete_account':
            confirm_text = request.POST.get('deleteConfirm', '').strip()
            if confirm_text == 'DELETE':
                user.is_active = False
                user.save()
                logout(request)
                messages.error(request, "Your account has been permanently closed.")
                return redirect('home')
            else:
                messages.error(request, "You must type DELETE exactly to confirm.")
                tab = 'danger'

    # ════════════════════════════════
    #  NEW: BILLING DATA FETCHING
    # ════════════════════════════════
    
    # 1. Fetch or create Subscription (Handles old accounts gracefully)
    try:
        subscription = company_profile.subscription
        # Dynamically check and update expired subscriptions
        if subscription.status == 'Active' and subscription.end_date and subscription.end_date < timezone.now():
            subscription.status = 'Expired'
            subscription.save()
    except CompanySubscription.DoesNotExist:
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free", 
            defaults={'price': 0, 'job_post_limit': 3, 'monthly_credits': 0}
        )
        subscription = CompanySubscription.objects.create(
            company=company_profile, 
            current_plan=free_plan, 
            status='Active'
        )

    # 2. Fetch or create Credits
    try:
        credits = company_profile.credits
    except CompanyCredit.DoesNotExist:
        credits = CompanyCredit.objects.create(company=company_profile, available_credits=0)

    # 3. Fetch Payment History
    payment_logs = PaymentLog.objects.filter(company=company_profile).order_by('-timestamp')

    # 4. Fetch active paid plans and Professional plan (as fallback)
    plans = SubscriptionPlan.objects.filter(is_active=True).exclude(price=0).order_by('price')
    pro_plan = SubscriptionPlan.objects.filter(name__icontains='Professional').first()

    context = {
        'tab': tab,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'subscription': subscription,  # Passed to template
        'credits': credits,            # Passed to template
        'payment_logs': payment_logs,  # Passed to template
        'plans': plans,                # Passed to template
        'pro_plan': pro_plan,          # Passed to template
    }
    
    return render(request, "company/company_account_setting.html", context)
# @login_required(login_url='login')
# def company_account_settings(request):
#     # Read active tab from query params, default to myprofile
#     tab = request.GET.get('tab', 'myprofile')
#     user = request.user
    
#     # Get or fetch company profile safely
#     company_profile, _ = CompanyProfile.objects.get_or_create(user=user)

#     # Initialize forms for GET requests
#     user_form = CompanyUserUpdateForm(instance=user)
#     profile_form = CompanyProfileUpdateForm(instance=company_profile)
#     password_form = PasswordChangeForm(user=user)

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         # 1. MY PROFILE Form Handling
#         if action == 'update_profile':
#             user_form = CompanyUserUpdateForm(request.POST, instance=user)
#             profile_form = CompanyProfileUpdateForm(request.POST, request.FILES, instance=company_profile)
            
#             if user_form.is_valid() and profile_form.is_valid():
#                 user_form.save()
#                 profile_form.save()
#                 messages.success(request, "Your profile has been updated successfully.")
#                 return redirect(f"{request.path}?tab=myprofile")
#             else:
#                 messages.error(request, "Please correct the errors below.")
#                 tab = 'myprofile'

#         # 2. SECURITY Form Handling
#         elif action == 'change_password':
#             password_form = PasswordChangeForm(user=user, data=request.POST)
#             if password_form.is_valid():
#                 updated_user = password_form.save()
#                 update_session_auth_hash(request, updated_user) # Keeps user logged in after pass change
#                 messages.success(request, "Your password was successfully updated!")
#                 return redirect(f"{request.path}?tab=security")
#             else:
#                 messages.error(request, "Password update failed. Please check the requirements.")
#                 tab = 'security'

#         # 3. NOTIFICATIONS Form Handling (Mock/Fallback)
#         elif action == 'update_notifications':
#             # Integrate with actual model fields here when available
#             messages.success(request, "Notification preferences saved.")
#             return redirect(f"{request.path}?tab=notifications")

#         # 5. DANGER ZONE Form Handling
#         elif action == 'deactivate_account':
#             # Safe logical disable
#             user.is_active = False
#             user.save()
#             logout(request)
#             messages.info(request, "Your account has been deactivated.")
#             return redirect('login')

#         elif action == 'delete_account':
#             confirm_text = request.POST.get('deleteConfirm', '').strip()
#             if confirm_text == 'DELETE':
#                 # SAFE DELETION: Logical soft delete strictly enforced
#                 user.is_active = False
#                 user.save()
#                 logout(request)
#                 messages.error(request, "Your account has been permanently closed.")
#                 return redirect('home')
#             else:
#                 messages.error(request, "You must type DELETE exactly to confirm.")
#                 tab = 'danger'

#     # 4. BILLING Context Variables
#     billing_context = {
#         'plan_name': 'Pro Tier',
#         'plan_status': 'Active',
#         'plan_price': 'PKR 2,999'
#     }

#     context = {
#         'tab': tab,
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'password_form': password_form,
#         'billing': billing_context,
#     }
    
#     return render(request, "company/company_account_setting.html", context)