from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("COMPANY",   "Company"),
        ("CANDIDATE", "Candidate"),
        ('ADMIN','admin')
    )
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CANDIDATE")
    is_approved = models.BooleanField(default=False)
    phone       = models.CharField(max_length=20, blank=True, null=True)
    def save(self, *args, **kwargs):

        # agar user superuser hai to role automatically ADMIN ho
        if self.is_superuser:
            self.role = "ADMIN"
            self.is_approved=True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"




class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE ,related_name="company_profile")
    

    STATUS_CHOICES = (
        ("PENDING",   "Pending Review"),
        ("APPROVED",  "Approved"),
        ("REJECTED",  "Rejected"),
        ("ROLLBACK",  "Rollback — Needs Correction"),
    )
    company_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        blank=True,
        null=True
    )
    feedback = models.TextField(blank=True, null=True) #for admin feedback to company

    # Owner Info
    designation     = models.CharField(max_length=100, blank=True)
    # company_name=models.CharField(max_length=20, blank=True)

    # Company Info
    trade_name      = models.CharField(max_length=200, blank=True)
    legal_name      = models.CharField(max_length=200, blank=True)
    ntn_number      = models.CharField(max_length=50,  blank=True)
    company_email   = models.EmailField(blank=True)
    company_type    = models.CharField(max_length=50,  blank=True)
    industry        = models.CharField(max_length=100, blank=True)
    total_employees = models.CharField(max_length=20,  blank=True)
    landline        = models.CharField(max_length=30,  blank=True)
    company_phone   = models.CharField(max_length=20,  blank=True)
    est_date        = models.DateField(null=True, blank=True)
    website         = models.URLField(blank=True)

    # Location
    country         = models.CharField(max_length=5,   blank=True)
    province        = models.CharField(max_length=100, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    postal_code     = models.CharField(max_length=12,  blank=True)
    legal_address   = models.TextField(blank=True)

    # Overview
    overview        = models.TextField(blank=True)
    vision          = models.TextField(blank=True)

    # Logo
    logo            = models.ImageField(upload_to="company_logos/", null=True, blank=True)

    # Social Media
    facebook        = models.URLField(blank=True)
    twitter         = models.URLField(blank=True)
    linkedin        = models.URLField(blank=True)
    pinterest       = models.URLField(blank=True)

    # Admin feedback — REJECT + ROLLBACK 
    # rejection_reason = models.TextField(blank=True)
    # admin_message    = models.TextField(blank=True)   # rollback ya reject ka message
    # rejected_fields  = models.JSONField(default=dict, blank=True)
    # Format: {
    #   "trade_name": "Name is incorrect",
    #   "logo":       "Logo is blurry",
    #   "ntn_number": "Invalid NTN"
    # }
    

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name        = "Company Profile"
        verbose_name_plural = "Company Profiles"


class CompanyRejection(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='rejections')
    message = models.TextField(blank=True, null=True)     # Admin ka main message
    created_at = models.DateTimeField(auto_now_add=True)

    # Boolean fields bina JSON ke rejected fields track karne ke liye
    trade_name = models.BooleanField(default=False)
    legal_name = models.BooleanField(default=False)
    ntn_number = models.BooleanField(default=False)
    company_email = models.BooleanField(default=False)
    company_type = models.BooleanField(default=False)
    industry = models.BooleanField(default=False)
    website = models.BooleanField(default=False)
    country = models.BooleanField(default=False)
    province = models.BooleanField(default=False)
    city = models.BooleanField(default=False)
    legal_address = models.BooleanField(default=False)
    overview = models.BooleanField(default=False)
    logo = models.BooleanField(default=False)

    def __str__(self):
        return f"Rejection for {self.company.trade_name or self.company.legal_name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"