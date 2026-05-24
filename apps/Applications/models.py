from django.db import models
from accounts.models import CustomUser
from accounts.models import CompanyProfile
from candidate.models import CandidateProfile
from Jobs.models import Job
# Create your models here.
class Applications(models.Model): 
    STATUS_CHOICES = (
        ("APPLIED","Applied"), 
        ("REVIEWING", 'Reviewing'), 
        ("SHORTLISTED","Shortlisted"),
        ("INTERVIEW", "Interview"),
        ("OFFERED", "Offered"),
        ("HIRED","Hired"),
        ("REJECTED", "Rejected"),
        ("WITHDRAWN", "Withdrawn"),
    )
    candidate = models.ForeignKey(CandidateProfile, on_delete=models. CASCADE, related_name="applications") 
    job = models.ForeignKey(Job, on_delete=models. CASCADE, related_name='applications') 
    cover_letter = models.TextField(null=True, blank=True)
    resume_snapshot=models.FileField(upload_to='applications/resumes/', null=True, blank=True) 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="APPLIED") 
    company_notes = models.TextField(null=True, blank=True) 
    interview_date = models.DateTimeField(null=True, blank=True) 
    interview_link= models.URLField(null=True, blank=True)
    applied_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    is_seen_by_company =models.BooleanField(default=False)

    class Meta:
        unique_together = ('candidate', 'job')
        ordering = ["-applied_at"]

class ApplicationStatusHistory(models.Model):
    """Isrutable audit trail for every status change."""
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, related_name="history")
    old_status=models.CharField(max_length=30)
    new_status= models.CharField(max_length=30)
    changed_by= models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    note  = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)




