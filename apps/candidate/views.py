from django.shortcuts import render, redirect
from job.models import JobPost
# from .decorators import candidate_login_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    CandidateProfile, ProfessionalInfo, LocationInfo,
    AboutMe, Resume, Skill, Education, WorkExperience, SocialLinks
)
from .forms import (
    CandidateProfileForm, ProfessionalInfoForm, LocationInfoForm,
    AboutMeForm, ResumeForm, SocialLinksForm, EducationForm, WorkExperienceForm
)
from applications.models import Applications

@login_required
def candidate_dashboard(request):
    candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        # Applications
    applications = Applications.objects.filter(
        candidate=candidate
    ).select_related('job', 'job__company').order_by('-applied_at')

    # Stats
    total_applied = applications.count()

    featured_jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company").order_by("-created_at")[:6]
    context={
        "featured_jobs": featured_jobs,
        "candidate": candidate,
        "applications":  applications,
        "total_applied": total_applied,
    }

    return render(request, 'candidate/candidate_dashboard.html', context)


# @candidate_login_required
# def profile(request):
#     return render(request, 'candidate/profile.html')
# CANDIDATE DASHBOARD
def candidate_base(request):
    return render(request, "candidate/candidate_base.html")

# def candidate_edit_profile(request):
#     return render(request,"candidate/candidate_edit_profile.html")

@login_required
def candidate_edit_profile(request):
    # Profile exist kare ya create ho
    candidate, created = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.username,
            "email": request.user.email,
            "phone_number": request.user.phone or "",
        }
    )

    context = {
        'candidate': candidate,
        # Related objects — exist na karein toh None ayega
        'professional': getattr(candidate, 'professional_info', None),
        'location':     getattr(candidate, 'location_info', None),
        'about':        getattr(candidate, 'about_me', None),
        'resume':       getattr(candidate, 'resume', None),
        'skills':       candidate.skills.all(),
        'educations':   candidate.educations.all(),
        'experiences':  candidate.work_experiences.all(),
        'social':       getattr(candidate, 'social_links', None),
    }
    return render(request, 'candidate/candidate_edit_profile.html', context)


# ── Personal Info ──
def save_personal_info(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal info save ho gayi!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_save_personal_info')


def save_professional_info(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        prof, _ = ProfessionalInfo.objects.get_or_create(candidate=candidate)
        form = ProfessionalInfoForm(request.POST, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, "Professional info save ho gayi!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:save_professional_info')


def save_location(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        loc, _ = LocationInfo.objects.get_or_create(candidate=candidate)
        form = LocationInfoForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            messages.success(request, "Location save ho gayi!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:save_location')


def save_about_me(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        about, _ = AboutMe.objects.get_or_create(candidate=candidate)
        form = AboutMeForm(request.POST, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, "About Me save ho gaya!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:save_about_me')


def save_resume(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        resume, _ = Resume.objects.get_or_create(candidate=candidate)
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume save ho gaya!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:save_resume')


def save_skills(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        skills_raw = request.POST.get('skills_data', '')
        skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
        candidate.skills.all().delete()
        for skill_name in skill_list:
            Skill.objects.create(candidate=candidate, skill_name=skill_name)
        messages.success(request, "Skills save ho gayi!")
    return redirect('candidate:save_skills')
    # Skills ka form nahi banaya — simple hai, direct theek hai


def save_education(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        candidate.educations.all().delete()
        degrees      = request.POST.getlist('degree')
        institutions = request.POST.getlist('institution_name')
        start_years  = request.POST.getlist('start_year')
        end_years    = request.POST.getlist('end_year')
        grades       = request.POST.getlist('grade_cgpa')
        for i in range(len(degrees)):
            if degrees[i]:
                # Basic validation
                try:
                    Education.objects.create(
                        candidate        = candidate,
                        degree           = degrees[i],
                        institution_name = institutions[i] if i < len(institutions) else '',
                        start_year       = int(start_years[i]) if start_years[i] else 2000,
                        end_year         = int(end_years[i]) if end_years[i] else None,
                        grade_cgpa       = grades[i] if i < len(grades) else '',
                    )
                except Exception as e:
                    messages.error(request, f"Education entry {i+1} mein error: {e}")
                    return redirect('candidate:candidate_edit_profile')
        messages.success(request, "Education save ho gayi!")
    return redirect('candidate:save_education')
    # Education/Experience ka bhi form nahi — multiple entries hain, direct theek hai


def save_experience(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        candidate.work_experiences.all().delete()
        job_titles  = request.POST.getlist('job_title')
        companies   = request.POST.getlist('company_name')
        start_dates = request.POST.getlist('start_date')
        end_dates   = request.POST.getlist('end_date')
        emp_types   = request.POST.getlist('employment_type')
        for i in range(len(job_titles)):
            if job_titles[i]:
                try:
                    WorkExperience.objects.create(
                        candidate       = candidate,
                        job_title       = job_titles[i],
                        company_name    = companies[i] if i < len(companies) else '',
                        start_date      = start_dates[i] if start_dates[i] else None,
                        end_date        = end_dates[i] if end_dates[i] else None,
                        employment_type = emp_types[i] if i < len(emp_types) else '',
                    )
                except Exception as e:
                    messages.error(request, f"Experience entry {i+1} mein error: {e}")
                    return redirect('candidate:candidate_edit_profile')
        messages.success(request, "Experience save ho gayi!")
    return redirect('candidate:save_experience')


def save_social_links(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        social, _ = SocialLinks.objects.get_or_create(candidate=candidate)
        form = SocialLinksForm(request.POST, instance=social)
        if form.is_valid():
            form.save()
            messages.success(request, "Social links save ho gayi!")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('candidate:save_social_links')


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