from django.db import models
from accounts.models import CompanyProfile


class JobPost(models.Model):

    STATUS_CHOICES = [
        ("PENDING_REVIEW", "Pending Review"),
        ("PUBLISHED",      "Published"),
        ("DRAFT",          "Draft"),
        ("CLOSED",         "Closed"),
        ("REJECTED",       "Rejected"),
    ]
    VISIBILITY_CHOICES = [
        ("public",  "Public"),
        ("private", "Private"),
    ]
    SALARY_TYPE_CHOICES = [
        ("range",       "Salary Range"),
        ("fixed",       "Fixed Amount"),
        ("negotiable",  "Negotiable"),
        ("unpaid",      "Unpaid"),
    ]

    # ── Relationship ──
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    # ── Step 1: Basic Info ──
    title             = models.CharField(max_length=255)
    category          = models.CharField(max_length=100)
    experience_level  = models.CharField(max_length=50)
    job_type          = models.CharField(max_length=50)          # Full-Time, Part-Time, etc.
    location          = models.CharField(max_length=150)
    work_mode         = models.CharField(max_length=50)          # On-site, Remote, Hybrid
    deadline          = models.DateField()
    vacancies         = models.IntegerField(default=1)

    # ── Step 2: Requirements ──
    description       = models.TextField()
    qualifications    = models.TextField()
    minimum_education = models.CharField(max_length=100, blank=True)
    years_of_experience = models.CharField(max_length=50, blank=True)
    skills            = models.TextField(blank=True)             # comma-separated e.g. "Python,Django,React"
    responsibilities  = models.TextField(blank=True, null=True)

    # ── Step 3: Compensation ──
    salary_type       = models.CharField(max_length=50, choices=SALARY_TYPE_CHOICES, default="range")
    currency          = models.CharField(max_length=10, default="PKR")
    salary_min        = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max        = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_fixed      = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    perks             = models.TextField(blank=True)             # comma-separated
    additional_notes  = models.TextField(blank=True, null=True)

    # ── Meta ──
    visibility        = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public")
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING_REVIEW")
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    # ── Helpers ──
    def get_skills_list(self):
        """Return skills as Python list."""
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def get_perks_list(self):
        """Return perks as Python list."""
        return [p.strip() for p in self.perks.split(",") if p.strip()]

    def salary_display(self):
        """Human-readable salary string."""
        if self.salary_type == "negotiable":
            return "Negotiable"
        if self.salary_type == "unpaid":
            return "Unpaid Internship"
        if self.salary_type == "fixed" and self.salary_fixed:
            return f"{self.currency} {self.salary_fixed:,.0f} / month"
        if self.salary_type == "range" and self.salary_min and self.salary_max:
            return f"{self.currency} {self.salary_min:,.0f} – {self.salary_max:,.0f} / month"
        return "—"

    def __str__(self):
        return f"{self.title} — {self.company.trade_name or self.company.user.username}"

    class Meta:
        ordering            = ["-created_at"]
        verbose_name        = "Job Post"
        verbose_name_plural = "Job Posts"