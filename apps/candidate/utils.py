from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone

try:
    from weasyprint import HTML
    PDF_ENABLED = True
except (ImportError, OSError):
    PDF_ENABLED = False


def calculate_profile_completion(candidate):
    fields = [
        bool(candidate.first_name and candidate.last_name),
        hasattr(candidate, 'professional_info') and bool(candidate.professional_info.job_title),
        hasattr(candidate, 'location_info') and bool(candidate.location_info.city),
        hasattr(candidate, 'about_me') and bool(candidate.about_me.professional_summary),
        hasattr(candidate, 'resume') and bool(candidate.resume.file),
        candidate.skills.exists(),
        candidate.educations.exists(),
        candidate.work_experiences.exists(),
    ]
    return int((sum(fields) / len(fields)) * 100)


def generate_resume_pdf(candidate):
    """Renders viewresume.html to PDF and saves it on the candidate."""
    if not PDF_ENABLED:
        return False  # silently skip — native libs not available yet

    html_string = render_to_string("candidate/viewresume_pdf.html", {
        "candidate": candidate,
        "educations": candidate.educations.all(),
        "experiences": candidate.work_experiences.all(),
        "skills": candidate.skills.all(),
        "about": getattr(candidate, "about_me", None),
        "professional": getattr(candidate, "professional_info", None),
        "social": getattr(candidate, "social_links", None),
        "location": getattr(candidate, "location_info", None),
    })

    pdf_bytes = HTML(string=html_string).write_pdf()
    filename = f"{candidate.username}_resume.pdf"

    candidate.generated_resume_pdf.save(filename, ContentFile(pdf_bytes), save=False)
    candidate.resume_pdf_updated_at = timezone.now()
    candidate.save(update_fields=["generated_resume_pdf", "resume_pdf_updated_at"])
    return True


def check_and_generate_pdf(candidate):
    if not PDF_ENABLED:
        return
    if calculate_profile_completion(candidate) == 100:
        generate_resume_pdf(candidate)