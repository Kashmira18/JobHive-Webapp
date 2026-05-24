from django.db import models
from accounts.models import CompanyProfile
from candidate.models import CandidateProfile
# Create your models here.
class Industries(models.Model):
    name =models.CharField(max_length=255, null=True, blank=True)
    slug=models.SlugField(max_length=255, null=True, blank=True)


class JobCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug= models.SlugField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)

class Skills (models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)


class Job(models.Model):
    STATUS=(
        ('draft', 'Draft'),
        ('published', 'Published'),
        ("closed", "Closed"),
        ('expired', 'Expired'),
    )

    job_type=(
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ("contract", "Contract"),
        ('temporary', 'Temporary'),
        ('other','Other')
    )
    experience_level=(
        ('entry-level','Entry-level')
        ('mid-level','Mid-level')
        ('senior-level','Senior-level')
        ('lead-level','Lead-level')
        ('executive-level','Executive-level')

    )

    company = models.ForeignKey(CompanyProfile,on_delete=models. CASCADE, null=True, blank=True, related_name="jobs")
    title = models.CharField(max_length=255, null=True, blank=True)
    slug= models. SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    category= models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True) 
    job_type = models.CharField(max_length=50, choices=job_type, null=True, blank=True) 
    salary_min= models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) 
    salary_max= models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    experience_level = models.CharField(max_length=50, choices=experience_level, null=True, blank=True)
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    skills = models.ManyToManyField(Skills, blank=True)
    industry = models.ForeignKey(Industries, on_delete=models.SET_NULL, null=True, blank=True) 
    location = models.CharField(max_length=255, null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    vacanies = models.IntegerField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')

    
    view_count = models.PositiveIntegerField(default=0) 
    applicant_count = models. PositiveIntegerField(default=0) 
    is_featured=models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True) 
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status','published_at']),
            models.Index(fields=['company','status']),
        ]


class JobSkill(models.Model):
    job= models.ForeignKey(Job, on_delete=models. CASCADE) 
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE) 
    is_required = models.BooleanField(default=True)

class SavedJob(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job= models.ForeignKey(Job, on_delete=models. CASCADE, related_name='saved_by') 
    saved_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('candidate', 'job')
        