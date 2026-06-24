from django.db import models
from accounts.models import CustomUser
# Create your models here.

# 1. CANDIDATE PROFILE  personal info
class CandidateProfile(models.Model):
    GENDER_CHOICES = [
        ('MALE',   'Male'),
        ('FEMALE', 'Female'),
        ('OTHER',  'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='candidate_profile')

    # Profile photo
    profile_photo = models.ImageField(upload_to='candidate/profile_photos/', blank=True, null=True)

    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    cnic_number = models.CharField(max_length=15, blank=True)          #like 35202-1234567-1
    id_card_front = models.FileField(upload_to='candidate/id_cards/', blank=True, null=True)
    id_card_back  = models.FileField(upload_to='candidate/id_cards/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


# 2. PROFESSIONAL INFORMATION
class ProfessionalInfo(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('freelance',  'Freelance'),
        ('internship', 'Internship'),
        ('remote',     'Remote'),
        ('contract',   'Contract'),
    ]

    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='professional_info')
    job_title = models.CharField(max_length=150, blank=True)
    industry = models.CharField(max_length=150, blank=True)
    years_of_experience = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    job_type_preference = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True)
    availability=models.CharField(max_length=50, null=True, blank=True) #Extra Field dalni hy abi
    def __str__(self):
        return f"{self.candidate.username} – {self.job_title}"


# 3. LOCATION INFORMATION

class LocationInfo(models.Model):
    candidate    = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='location_info')
    province     = models.CharField(max_length=100)
    city         = models.CharField(max_length=100)
    postal_code  = models.CharField(max_length=20, blank=True)
    full_address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.city}, {self.province}"


# 4. ABOUT ME  (summary & objective)
class AboutMe(models.Model):
    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='about_me')
    professional_summary = models.TextField(blank=True)
    career_objective = models.TextField(blank=True)
    profile_completion = models.PositiveSmallIntegerField(default=0) #ya wali filed dalni hy abi 

    def __str__(self):
        return f"About – {self.candidate.username}"


# 5. RESUME / CV
class Resume(models.Model):
    candidate = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='resume')
    file = models.FileField(upload_to='candidate/resumes/') # PDF or DOCX, max 5 MB (enforce in form/serializer)
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume – {self.candidate.username}"

# 6. SKILLS
class Skill(models.Model):
    profiency_level = (
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced","Advanced"),
        ("Expert","Expert"),
   )
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='skills')
    skill_name= models.CharField(max_length=100, null=True, blank=True)
    proficiency=models.CharField(max_length=50, choices=profiency_level, null=True, blank=True) #Extra Field dalni hy abi

    class Meta:
        unique_together = ('candidate', 'skill_name')

    def __str__(self):
        return self.name


# 7. EDUCATION
class Education(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    institution_name = models.CharField(max_length=200)
    field_of_study= models.CharField(max_length=200, blank=True, null=True) #Extra Field dalni hy abi
    start_year= models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    grade_cgpa = models.CharField(max_length=20, blank=True)        # e.g. "3.5 / 4.0"


    class Meta:
        ordering = ['-end_year']

    def __str__(self):
        return f"{self.degree} – {self.institution_name}"


# 8. WORK EXPERIENCE

class WorkExperience(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('freelance',  'Freelance'),
        ('internship', 'Internship'),
        ('contract',   'Contract'),
    ]

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='work_experiences')
    job_title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)   # null = currently working
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True)
    achievements= models.CharField(blank=True, null=True) #Extra Field dalni hy abi
    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} @ {self.company_name}"
    
# 9.CERTIFICATES Ya wala kam dalna hy abi

class CandidateCertification (models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='certification')
    name = models.CharField(max_length=255, null=True, blank=True)
    issuing_organization=models.CharField(max_length=255, null=True, blank=True)
    issue_date= models.DateField(null=True, blank=True)
    expiration_date= models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=255, null=True, blank=True) 
    credential_url = models.URLField(null=True, blank=True)


# 10. SOCIAL & PORTFOLIO LINKS
class SocialLinks(models.Model):
    candidate  = models.OneToOneField(CandidateProfile, on_delete=models.CASCADE, related_name='social_links')
    github  = models.URLField(blank=True)
    twitter_x = models.URLField(blank=True)
    linkedin  = models.URLField(blank=True)
    portfolio  = models.URLField(blank=True)

    def __str__(self):
        return f"Links – {self.candidate.username}"
