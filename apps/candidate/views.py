from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from job.models import JobPost
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


def candidate_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access your candidate dashboard.")
            return redirect('accounts:login')

        if getattr(request.user, 'role', None) != 'CANDIDATE':
            messages.error(request, "This area is only available to candidates.")
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def get_or_create_candidate_profile(user):
    candidate, _ = CandidateProfile.objects.get_or_create(
        user=user,
        defaults={
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or user.username,
            'last_name': user.last_name or '',
            'phone_number': getattr(user, 'phone', '') or '',
        },
    )
    return candidate


def get_profile_photo_url(profile):
    if getattr(profile, 'profile_photo', None) and profile.profile_photo.name:
        return profile.profile_photo.url
    return static('images/default-avatar.svg')


def calculate_candidate_completion(candidate):
    professional = getattr(candidate, 'professional_info', None)
    location = getattr(candidate, 'location_info', None)
    about = getattr(candidate, 'about_me', None)
    resume = getattr(candidate, 'resume', None)

    fields = [
        bool(getattr(candidate, 'first_name', '') and getattr(candidate, 'last_name', '')),
        bool(professional and getattr(professional, 'job_title', '')),
        bool(location and getattr(location, 'city', '')),
        bool(about and getattr(about, 'professional_summary', '')),
        bool(resume and getattr(resume, 'file', '')),
        candidate.skills.exists(),
        candidate.educations.exists(),
        candidate.work_experiences.exists(),
    ]
    return int((sum(fields) / len(fields)) * 100) if fields else 0


@login_required
@candidate_required
def candidate_dashboard(request):
    candidate = get_or_create_candidate_profile(request.user)
    candidate = get_object_or_404(CandidateProfile, user=request.user)
    profile_photo_url = get_profile_photo_url(candidate)

    applications = Applications.objects.filter(candidate=candidate).select_related('job', 'job__company').order_by('-applied_at')
    recent_applications = applications[:3]
    total_applied = applications.count()
    shortlisted_applications = applications.filter(status='SHORTLISTED').count()
    saved_jobs = 0
    profile_views = 0

    status_breakdown = {status: 0 for status, _label in Applications.STATUS_CHOICES}
    for application in applications.values_list('status', flat=True):
        status_breakdown[application] = status_breakdown.get(application, 0) + 1

    recent_notifications = []
    try:
        from notifications.models import Notification
        recent_notifications = list(Notification.objects.filter(user=request.user).order_by('-created_at')[:5])
    except Exception:
        recent_notifications = []

    completion_percentage = calculate_candidate_completion(candidate)

    featured_jobs = JobPost.objects.filter(
        status='PUBLISHED',
        visibility='public',
    ).select_related('company').order_by('-created_at')[:6]

    skill_names = list(candidate.skills.values_list('skill_name', flat=True))
    if skill_names:
        skill_q = Q()
        for skill in skill_names:
            skill_q |= Q(title__icontains=skill) | Q(description__icontains=skill)
        recommended_jobs = JobPost.objects.filter(
            skill_q,
            status='PUBLISHED',
            visibility='public',
        ).exclude(id__in=featured_jobs.values_list('id', flat=True)).distinct()[:6]
    else:
        recommended_jobs = JobPost.objects.none()

    context = {
        'recommended_jobs': recommended_jobs,
        'featured_jobs': featured_jobs,
        'candidate': candidate,
        'profile': candidate,
        'profile_photo_url': profile_photo_url,
        'applications': applications,
        'total_applied': total_applied,
        'shortlisted_applications': shortlisted_applications,
        'saved_jobs': saved_jobs,
        'profile_views': profile_views,
        'completion_percentage': completion_percentage,
        'recent_applications': recent_applications,
        'status_breakdown': status_breakdown,
        'recent_notifications': recent_notifications,
        'resume_file': getattr(getattr(candidate, 'resume', None), 'file', None),
    }

    return render(request, 'candidate/candidate_dashboard.html', context)

@login_required
@candidate_required
def candidate_edit_profile(request):
    profile = get_or_create_candidate_profile(request.user)
    profile = get_object_or_404(CandidateProfile, user=request.user)
    profile_photo_url = get_profile_photo_url(profile)

    if request.method == 'POST':
        section = request.POST.get('section') or 'profile'
        if section in {'profile', 'personal'}:
            form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

        if section == 'professional':
            professional = getattr(profile, 'professional_info', None) or ProfessionalInfo(candidate=profile)
            form = ProfessionalInfoForm(request.POST, instance=professional)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

        if section == 'location':
            location = getattr(profile, 'location_info', None) or LocationInfo(candidate=profile)
            form = LocationInfoForm(request.POST, instance=location)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

        if section == 'about':
            about = getattr(profile, 'about_me', None) or AboutMe(candidate=profile)
            form = AboutMeForm(request.POST, instance=about)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

        if section == 'resume':
            resume = getattr(profile, 'resume', None) or Resume(candidate=profile)
            form = ResumeForm(request.POST, request.FILES, instance=resume)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

        if section == 'skills':
            skills_raw = request.POST.get('skills', '')
            skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
            profile.skills.all().delete()
            for skill_name in skill_list:
                Skill.objects.create(candidate=profile, skill_name=skill_name)
            profile.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('candidate:candidate_edit_profile')

        if section == 'education':
            degree_list = request.POST.getlist('degree[]') or request.POST.getlist('education_set-0-degree')
            institution_list = request.POST.getlist('institution[]') or request.POST.getlist('education_set-0-institution_name')
            start_year_list = request.POST.getlist('start_year[]') or request.POST.getlist('education_set-0-start_year')
            end_year_list = request.POST.getlist('end_year[]') or request.POST.getlist('education_set-0-end_year')
            grade_list = request.POST.getlist('grade[]') or request.POST.getlist('education_set-0-grade_cgpa')

            profile.educations.all().delete()
            for i in range(max(len(degree_list), len(institution_list), len(start_year_list), len(end_year_list), len(grade_list))):
                degree = (degree_list[i] if i < len(degree_list) else '').strip()
                institution = (institution_list[i] if i < len(institution_list) else '').strip()
                start_year = (start_year_list[i] if i < len(start_year_list) else '').strip()
                end_year = (end_year_list[i] if i < len(end_year_list) else '').strip()
                grade = (grade_list[i] if i < len(grade_list) else '').strip()
                if not degree and not institution and not start_year and not end_year and not grade:
                    continue
                Education.objects.create(
                    candidate=profile,
                    degree=degree,
                    institution_name=institution,
                    start_year=int(start_year) if start_year else 0,
                    end_year=int(end_year) if end_year else None,
                    grade_cgpa=grade,
                )

            messages.success(request, 'Section updated successfully!')
            return redirect('candidate:candidate_edit_profile')

        if section == 'experience':
            job_titles = request.POST.getlist('job_title[]') or request.POST.getlist('job_title')
            company_names = request.POST.getlist('company_name[]') or request.POST.getlist('company_name')
            start_dates = request.POST.getlist('start_date[]') or request.POST.getlist('start_date')
            end_dates = request.POST.getlist('end_date[]') or request.POST.getlist('end_date')
            employment_types = request.POST.getlist('employment_type[]') or request.POST.getlist('employment_type')
            descriptions = request.POST.getlist('job_description[]') or request.POST.getlist('achievements') or request.POST.getlist('description')

            is_fresher = request.POST.get('is_fresher') == 'on'
            profile.is_fresher = is_fresher
            profile.save(update_fields=['is_fresher'])

            if is_fresher:
                profile.work_experiences.all().delete()
                messages.success(request, 'Section updated successfully!')
                return redirect('candidate:candidate_edit_profile')

            profile.work_experiences.all().delete()
            for i in range(max(len(job_titles), len(company_names), len(start_dates), len(end_dates), len(employment_types), len(descriptions))):
                job_title = (job_titles[i] if i < len(job_titles) else '').strip()
                company_name = (company_names[i] if i < len(company_names) else '').strip()
                start_date = (start_dates[i] if i < len(start_dates) else '').strip()
                end_date = (end_dates[i] if i < len(end_dates) else '').strip()
                employment_type = (employment_types[i] if i < len(employment_types) else '').strip()
                description = (descriptions[i] if i < len(descriptions) else '').strip()
                if not job_title and not company_name and not start_date and not end_date and not employment_type and not description:
                    continue
                if start_date and len(start_date) == 7:
                    start_date = f"{start_date}-01"
                if not start_date:
                    start_date = None

                if end_date and len(end_date) == 7:
                    end_date = f"{end_date}-01"
                if not end_date:
                    end_date = None

                try:
                    WorkExperience.objects.create(
                        candidate=profile,
                        job_title=job_title,
                        company_name=company_name,
                        start_date=start_date,
                        end_date=end_date,
                        employment_type=employment_type,
                        achievements=description,
                    )
                except Exception as e:
                    pass

            messages.success(request, 'Section updated successfully!')
            return redirect('candidate:candidate_edit_profile')

        if section == 'social':
            social = getattr(profile, 'social_links', None) or SocialLinks(candidate=profile)
            form = SocialLinksForm(request.POST, instance=social)
            if form.is_valid():
                form.save()
                messages.success(request, 'Section updated successfully!')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            return redirect('candidate:candidate_edit_profile')

    EducationFormSet = inlineformset_factory(CandidateProfile, Education, form=EducationForm, extra=0, can_delete=True)
    ExperienceFormSet = inlineformset_factory(CandidateProfile, WorkExperience, form=WorkExperienceForm, extra=0, can_delete=True)

    education_records = list(profile.educations.all())
    experience_records = list(profile.work_experiences.all())

    context = {
        'candidate': profile,
        'profile': profile,
        'profile_photo_url': profile_photo_url,
        'professional': getattr(profile, 'professional_info', None),
        'location': getattr(profile, 'location_info', None),
        'about': getattr(profile, 'about_me', None),
        'resume': getattr(profile, 'resume', None),
        'skills': profile.skills.all(),
        'educations': education_records,
        'education_formset': EducationFormSet(instance=profile, prefix='edu'),
        'experience_formset': ExperienceFormSet(instance=profile, prefix='exp'),
        'experiences': experience_records,
        'social': getattr(profile, 'social_links', None),
        'profile_form': CandidateProfileForm(instance=profile),
        'professional_form': ProfessionalInfoForm(instance=getattr(profile, 'professional_info', None)),
        'location_form': LocationInfoForm(instance=getattr(profile, 'location_info', None)),
        'about_form': AboutMeForm(instance=getattr(profile, 'about_me', None)),
        'resume_form': ResumeForm(instance=getattr(profile, 'resume', None)),
        'social_form': SocialLinksForm(instance=getattr(profile, 'social_links', None)),
    }
    return render(request, 'candidate/candidate_edit_profile.html', context)


# ── Personal Info ──
@login_required
@candidate_required
def save_personal_info(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        form = CandidateProfileForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal info saved!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_professional_info(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        prof, _ = ProfessionalInfo.objects.get_or_create(candidate=candidate)
        form = ProfessionalInfoForm(request.POST, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professional info saved!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_location(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        loc, _ = LocationInfo.objects.get_or_create(candidate=candidate)
        form = LocationInfoForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location saved')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_about_me(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        about, _ = AboutMe.objects.get_or_create(candidate=candidate)
        form = AboutMeForm(request.POST, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'About Me saved!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_resume(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        resume, _ = Resume.objects.get_or_create(candidate=candidate)
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resume saved!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_skills(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        skills_raw = request.POST.get('skills_data', '')
        skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
        candidate.skills.all().delete()
        for skill_name in skill_list:
            Skill.objects.create(candidate=candidate, skill_name=skill_name)
        messages.success(request, 'Skills saved!')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_education(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        EducationFormSet = inlineformset_factory(
            CandidateProfile, Education,
            form=EducationForm,
            extra=0, can_delete=True,
        )
        formset = EducationFormSet(request.POST, instance=candidate, prefix='edu')
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Education saved!')
        else:
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_experience(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        is_fresher = 'is_fresher' in request.POST
        ExperienceFormSet = inlineformset_factory(
            CandidateProfile, WorkExperience,
            form=WorkExperienceForm,
            extra=0, can_delete=True,
        )

        if is_fresher:
            candidate.work_experiences.all().delete()
            messages.success(request, 'Marked as fresher, experience cleared.')
        else:
            formset = ExperienceFormSet(request.POST, instance=candidate, prefix='exp')
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Experience is saved!')
            else:
                for form in formset:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')

    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def save_social_links(request):
    if request.method == 'POST':
        candidate = get_or_create_candidate_profile(request.user)
        social, _ = SocialLinks.objects.get_or_create(candidate=candidate)
        form = SocialLinksForm(request.POST, instance=social)
        if form.is_valid():
            form.save()
            messages.success(request, 'Social links are saved!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('candidate:candidate_edit_profile')


@login_required
@candidate_required
def bookmark_jobs(request):
    candidate = get_or_create_candidate_profile(request.user)
    applied = Applications.objects.filter(candidate=candidate).select_related('job', 'job__company').order_by('-applied_at')
    return render(request, 'candidate/Bookmark_Jobs.html', {'jobs': applied})


@login_required
@candidate_required
def applied_jobs(request):
    candidate = get_or_create_candidate_profile(request.user)
    applications = Applications.objects.filter(candidate=candidate).select_related('job', 'job__company').order_by('-applied_at')

    return render(request, 'candidate/applied_jobs.html', {'applications': applications})


@login_required
@candidate_required
def candidate_notifications(request):
    from notifications.models import Notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'candidate/notifications.html', {'notifications': notifications})


@login_required
@candidate_required
def candidate_view_resume(request):
    candidate = get_or_create_candidate_profile(request.user)
    educations = candidate.educations.all()
    experiences = candidate.work_experiences.all()
    skills = candidate.skills.all()
    about = getattr(candidate, 'about_me', None)
    professional = getattr(candidate, 'professional_info', None)
    social = getattr(candidate, 'social_links', None)
    location = getattr(candidate, 'location_info', None)
    return render(request, 'candidate/viewresume.html', {
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
@candidate_required
def candidate_setting(request):
    candidate = get_or_create_candidate_profile(request.user)
    return render(request, 'candidate/candidate_setting.html', {'candidate': candidate})


@login_required
@candidate_required
def messenger(request):
    return render(request, 'candidate/messenger.html')


@login_required
@candidate_required
def print_resume(request):
    """Print-friendly resume page — works without WeasyPrint (browser handles PDF via Ctrl+P)."""
    candidate = get_or_create_candidate_profile(request.user)
    return render(request, 'candidate/viewresume_pdf.html', {
        'candidate': candidate,
        'educations': candidate.educations.all(),
        'experiences': candidate.work_experiences.all(),
        'skills': candidate.skills.all(),
        'about': getattr(candidate, 'about_me', None),
        'professional': getattr(candidate, 'professional_info', None),
        'social': getattr(candidate, 'social_links', None),
        'location': getattr(candidate, 'location_info', None),
    })


@login_required
@candidate_required
def download_resume_pdf(request):
    candidate = get_or_create_candidate_profile(request.user)

    if not PDF_ENABLED:
        return redirect('candidate:print_resume')

    generate_resume_pdf(candidate)
    return FileResponse(candidate.generated_resume_pdf.open('rb'), as_attachment=True, filename=f'{candidate.username}_resume.pdf')
