from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("COMPANY",   "Company"),
        ("CANDIDATE", "Candidate"),
    )
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CANDIDATE")
    is_approved = models.BooleanField(default=False)   # sirf COMPANY ke liye
    phone       = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class CompanyProfile(models.Model):
    """
    Company ka extra profile — CustomUser se alag table.
    Ek company ka ek hi profile hoga (OneToOne).
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="company_profile"
    )

    # ── Owner Info ──
    designation     = models.CharField(max_length=100, blank=True)

    # ── Company Info ──
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

    # ── Location ──
    country         = models.CharField(max_length=5,   blank=True)
    province        = models.CharField(max_length=100, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    postal_code     = models.CharField(max_length=12,  blank=True)
    legal_address   = models.TextField(blank=True)

    # ── Overview ──
    overview        = models.TextField(blank=True)
    vision          = models.TextField(blank=True)

    # ── Logo ──
    logo            = models.ImageField(
        upload_to="company_logos/",
        null=True, blank=True
    )

    # ── Social Media ──
    facebook        = models.URLField(blank=True)
    twitter         = models.URLField(blank=True)
    linkedin        = models.URLField(blank=True)
    pinterest       = models.URLField(blank=True)

    # ── Timestamps ──
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trade_name or self.user.username} — Profile"

    class Meta:
        verbose_name        = "Company Profile"
        verbose_name_plural = "Company Profiles"
