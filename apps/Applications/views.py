from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from job.models import JobPost
from candidate.models import CandidateProfile, Resume
from .models import Applications
from .forms import JobApplicationForm
app_name = "applications" 
@login_required() 
def apply_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, status="PUBLISHED")
    candidate = request.user.candidate_profile
    # Check candidate profile exists
    try:
        candidate = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, "Please create your candidate profile first")
        return redirect('candidate:candidate_edit_profile')
    
    # Check profile is complete
    if not candidate.first_name or not candidate.last_name:
        messages.error(request, "Please fill your name first")
        return redirect('candidate:candidate_edit_profile')
    
    if not hasattr(candidate, 'location_info'):
        messages.error(request, "Please add your location first")
        return redirect('candidate:candidate_edit_profile')
    
    if not candidate.educations.exists():
        messages.error(request, "Please add your education first")
        return redirect('candidate:candidate_edit_profile')
    
    # Check not already applied
    if Applications.objects.filter(candidate=candidate, job=job).exists():
        messages.warning(request, "You already applied for this job")
        return redirect('job_detail', job_id=job.id)
    
    # Check if saved resume exists
    has_saved_resume = hasattr(candidate, 'resume')
    
    # FORM HANDLING
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            cover_letter = form.cleaned_data.get('cover_letter', '')
            resume_file = form.cleaned_data.get('resume_snapshot')
            
            # If no file uploaded, use saved resume
            if not resume_file:
                if has_saved_resume:
                    resume_file = candidate.resume.file
                else:
                    messages.error(request, "Please upload your resume")
                    return render(request, 'applications/apply.html', {
                        'form': form,
                        'job': job,
                        'has_saved_resume': has_saved_resume,
                    })
            
            # Create application
            application = Applications.objects.create(
                candidate=candidate,
                job=job,
                cover_letter=cover_letter,
                resume_snapshot=resume_file,
                status='APPLIED'
            )
            
            messages.success(request, "Application submitted successfully!")
            return redirect('application_success', app_id=application.id)
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = JobApplicationForm()
    
    return render(request, 'applications/apply.html', {
        'form': form,
        'job': job,
        'has_saved_resume': has_saved_resume,
    })


@login_required
def application_success(request, app_id):
    """Show success message after application submitted"""
    application = get_object_or_404(Applications, id=app_id)
    
    # Make sure only the user who applied can see it
    if application.candidate.user != request.user:
        messages.error(request, "Unauthorized access")
        return redirect('candidate_dashboard')
    
    return render(request, 'applications/success.html', {
        'application': application
    })