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
from django.forms import inlineformset_factory
from applications.models import Applications
from django.db.models import Q
from django.http import FileResponse
from .utils import generate_resume_pdf, PDF_ENABLED
@login_required
def candidate_dashboard(request):
    candidate, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "username":     request.user.username,
            "email":        request.user.email,
            "first_name":   request.user.first_name or request.user.username,
            "last_name":    request.user.last_name or "",
            "phone_number": "",
        }
    )

    # Applications
    applications = Applications.objects.filter(
        candidate=candidate
    ).select_related('job', 'job__company').order_by('-applied_at')

    recent_applications = applications[:3]

    # Stats
    total_applied = applications.count()
    shortlisted_applications = applications.filter(status='SHORTLISTED').count()
    saved_jobs = 0
    profile_views = 0

    # Calculate Profile Completion
    fields = [
        bool(candidate.first_name and candidate.last_name),
        hasattr(candidate, 'professional_info') and bool(candidate.professional_info.job_title),
        hasattr(candidate, 'location_info') and bool(candidate.location_info.city),
        hasattr(candidate, 'about_me') and bool(candidate.about_me.professional_summary),
        hasattr(candidate, 'resume') and bool(candidate.resume.file),
        candidate.skills.exists(),
        candidate.educations.exists(),
        candidate.work_experiences.exists()
    ]
    completion_percentage = int((sum(fields) / len(fields)) * 100)


    # Featured jobs (general)
    featured_jobs = JobPost.objects.filter(
        status="PUBLISHED",
        visibility="public"
    ).select_related("company").order_by("-created_at")[:6]

    # Recommended jobs based on candidate skills
    skill_names = list(candidate.skills.values_list('skill_name', flat=True))
    if skill_names:
        skill_q = Q()
        for skill in skill_names:
            skill_q |= Q(title__icontains=skill) | Q(description__icontains=skill)
        recommended_jobs = JobPost.objects.filter(
            skill_q,
            status="PUBLISHED",
            visibility="public"
        ).exclude(id__in=featured_jobs.values_list('id', flat=True)).distinct()[:6]
    else:
        recommended_jobs = JobPost.objects.none()


    context = {
        "recommended_jobs": recommended_jobs,
        "featured_jobs": featured_jobs,
        "candidate": candidate,
        "applications": applications,
        "total_applied": total_applied,
        "shortlisted_applications": shortlisted_applications,
        "saved_jobs": saved_jobs,
        "profile_views": profile_views,
        "completion_percentage": completion_percentage,
        "recent_applications": recent_applications,
    }

    return render(request, 'candidate/candidate_dashboard.html', context)

@login_required
def candidate_edit_profile(request):
    candidate, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.username,
            "email": request.user.email,
            "phone_number": request.user.phone or "",
        }
    )

    # ── Formsets ──
    EducationFormSet = inlineformset_factory(
        CandidateProfile, Education,
        form=EducationForm,
        extra=0, can_delete=True
    )
    ExperienceFormSet = inlineformset_factory(
        CandidateProfile, WorkExperience,
        form=WorkExperienceForm,
        extra=0, can_delete=True
    )

    context = {
        'candidate': candidate,
        'professional': getattr(candidate, 'professional_info', None),
        'location':     getattr(candidate, 'location_info', None),
        'about':        getattr(candidate, 'about_me', None),
        'resume':       getattr(candidate, 'resume', None),
        'skills':       candidate.skills.all(),
        'education_formset':   EducationFormSet(instance=candidate, prefix='edu'),
        'experience_formset':  ExperienceFormSet(instance=candidate, prefix='exp'),
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
            messages.success(request, "Personal info saved!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_professional_info(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        prof, _ = ProfessionalInfo.objects.get_or_create(candidate=candidate)
        form = ProfessionalInfoForm(request.POST, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, "Professional info saved!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_location(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        loc, _ = LocationInfo.objects.get_or_create(candidate=candidate)
        form = LocationInfoForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            messages.success(request, "Location saved")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_about_me(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        about, _ = AboutMe.objects.get_or_create(candidate=candidate)
        form = AboutMeForm(request.POST, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, "About Me saved!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_resume(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        resume, _ = Resume.objects.get_or_create(candidate=candidate)
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume saved!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_skills(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        skills_raw = request.POST.get('skills_data', '')
        skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
        candidate.skills.all().delete()
        for skill_name in skill_list:
            Skill.objects.create(candidate=candidate, skill_name=skill_name)
        messages.success(request, "Skills saved!")
    return redirect('candidate:candidate_edit_profile')
    # Skills ka form nahi banaya — simple hai, direct theek hai


def save_education(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        EducationFormSet = inlineformset_factory(
            CandidateProfile, Education,
            form=EducationForm,
            extra=0, can_delete=True
        )
        formset = EducationFormSet(request.POST, instance=candidate, prefix='edu')
        if formset.is_valid():
            formset.save()
            messages.success(request, "Education saved!")
        else:
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
    return redirect('candidate:candidate_edit_profile')


def save_experience(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        # Fresher/experience toggle save karo
        candidate.has_experience = 'is_fresher' not in request.POST
        candidate.save()
        ExperienceFormSet = inlineformset_factory(
            CandidateProfile, WorkExperience,
            form=WorkExperienceForm,
            extra=0, can_delete=True
        )
        if candidate.has_experience:
            formset = ExperienceFormSet(request.POST, instance=candidate, prefix='exp')
            if formset.is_valid():
                formset.save()
                messages.success(request, "Experience is saved!")
            else:
                for form in formset:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{error}")
        else:
            # Agar fresher select kiya to purani experience entries delete kar do
            candidate.work_experiences.all().delete()
            messages.success(request, "Marked as fresher, experience cleared.")

    return redirect('candidate:candidate_edit_profile')


def save_social_links(request):
    if request.method == 'POST':
        candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
        social, _ = SocialLinks.objects.get_or_create(candidate=candidate)
        form = SocialLinksForm(request.POST, instance=social)
        if form.is_valid():
            form.save()
            messages.success(request, "Social links are saved!")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('candidate:candidate_edit_profile')


@login_required
def bookmark_jobs(request):
    candidate, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "",
            "phone_number": "",
        }
    )
    # Until a dedicated SavedJob model is created, show recent applied jobs
    applied = Applications.objects.filter(candidate=candidate).select_related('job', 'job__company').order_by('-applied_at')
    return render(request, "candidate/Bookmark_Jobs.html", {'jobs': applied})
@login_required
def applied_jobs(request):

    candidate, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "",
            "phone_number": "",
        }
    )

    applications = Applications.objects.filter(
        candidate=candidate
    ).select_related(
        'job',
        'job__company'
    ).order_by('-applied_at')

    return render(
        request,
        'candidate/applied_jobs.html',
        {
            'applications': applications
        }
    )

@login_required
def candidate_notifications(request):
    from notifications.models import Notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "candidate/notifications.html", {'notifications': notifications})
@login_required
def candidate_view_resume(request):
    candidate, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name or request.user.username,
            "last_name": request.user.last_name or "",
            "phone_number": "",
        }
    )
    educations = candidate.educations.all()
    experiences = candidate.work_experiences.all()
    skills = candidate.skills.all()
    about = getattr(candidate, 'about_me', None)
    professional = getattr(candidate, 'professional_info', None)
    social = getattr(candidate, 'social_links', None)
    location = getattr(candidate, 'location_info', None)
    return render(request, "candidate/viewresume.html", {
        'candidate': candidate,
        'educations': educations,
        'experiences': experiences,
        'skills': skills,
        'about': about,
        'professional': professional,
        'social': social,
        'location': location,
    })
@login_required
def candidate_setting(request):
    candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
    return render(request, "candidate/candidate_setting.html", {'candidate': candidate})
def messenger(request):
    return render(request, 'candidate/messenger.html')
@login_required
def print_resume(request):
    """Print-friendly resume page — works without WeasyPrint (browser handles PDF via Ctrl+P)."""
    candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)
    return render(request, "candidate/viewresume_pdf.html", {
        "candidate": candidate,
        "educations": candidate.educations.all(),
        "experiences": candidate.work_experiences.all(),
        "skills": candidate.skills.all(),
        "about": getattr(candidate, "about_me", None),
        "professional": getattr(candidate, "professional_info", None),
        "social": getattr(candidate, "social_links", None),
        "location": getattr(candidate, "location_info", None),
    })


@login_required
def download_resume_pdf(request):
    candidate, _ = CandidateProfile.objects.get_or_create(user=request.user)

    if not PDF_ENABLED:
        # Fallback: send user to the print-friendly page instead of a real download
        return redirect('candidate:print_resume')

    generate_resume_pdf(candidate)
    return FileResponse(
        candidate.generated_resume_pdf.open('rb'),
        as_attachment=True,
        filename=f"{candidate.username}_resume.pdf"
    )
