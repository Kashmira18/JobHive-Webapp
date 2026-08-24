from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    CandidateProfile, ProfessionalInfo, LocationInfo,
    AboutMe, Resume, Skill, Education, WorkExperience
)
from .utils import check_and_generate_pdf

WATCHED_MODELS = [CandidateProfile, ProfessionalInfo, LocationInfo, AboutMe, Resume, Skill, Education, WorkExperience]


def _get_candidate(instance):
    return instance if isinstance(instance, CandidateProfile) else getattr(instance, "candidate", None)


@receiver(post_save)
@receiver(post_delete)
def auto_generate_pdf_on_change(sender, instance, **kwargs):
    if sender not in WATCHED_MODELS:
        return
    candidate = _get_candidate(instance)
    if candidate:
        check_and_generate_pdf(candidate)