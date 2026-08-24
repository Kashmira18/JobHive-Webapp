from django import forms
from job.models import JobPost, JobCategory
from django.contrib.auth import get_user_model
from accounts.models import CompanyProfile
from company.models import CompanyType

User = get_user_model()

class JobPostForm(forms.ModelForm):
    """
    ModelForm for JobPost — excludes company, status, created_at.
    These are set in the view.
    """
    class Meta:
        model  = JobPost
        exclude = ["company", "status", "created_at", "updated_at"]
        widgets = {
            # Step 1
            "title":            forms.TextInput(attrs={"id": "jobTitle", "placeholder": "e.g. Senior Frontend Developer"}),
            "category":         forms.Select(attrs={"id": "jobCategory"}),
            "experience_level": forms.Select(attrs={"id": "expLevel"}),
            "job_type":         forms.HiddenInput(attrs={"id": "jobTypeHidden"}),
            "location":         forms.TextInput(attrs={"id": "jobLocation", "placeholder": "e.g. Lahore, Pakistan"}),
            "work_mode":        forms.Select(attrs={"id": "workMode"}),
            "deadline":         forms.DateInput(attrs={"type": "date", "id": "deadline"}),
            "vacancies":        forms.NumberInput(attrs={"id": "vacancies", "min": "1"}),

            # Step 2
            "description":        forms.HiddenInput(attrs={"id": "descHidden"}),
            "qualifications":     forms.Textarea(attrs={"id": "qualifications", "rows": 3}),
            "minimum_education":  forms.Select(attrs={"id": "education"}),
            "years_of_experience":forms.Select(attrs={"id": "yearsExp"}),
            "skills":             forms.HiddenInput(attrs={"id": "skillsHidden"}),
            "responsibilities":   forms.Textarea(attrs={"id": "responsibilities", "rows": 3}),

            # Step 3
            "salary_type":     forms.Select(attrs={"id": "salaryType"}),
            "currency":        forms.Select(attrs={"id": "currency"}),
            "salary_min":      forms.NumberInput(attrs={"id": "salMin"}),
            "salary_max":      forms.NumberInput(attrs={"id": "salMax"}),
            "salary_fixed":    forms.NumberInput(attrs={"id": "salFixed"}),
            "perks":           forms.HiddenInput(attrs={"id": "perksHidden"}),
            "additional_notes":forms.Textarea(attrs={"id": "notes", "rows": 3}),

            # Meta
            "visibility": forms.RadioSelect(attrs={"name": "visibility"}),
        }

    # ── Choice fields defined manually for clean options ──
    CATEGORY_CHOICES = [
        ("", "Select category"),
    ]
    EXP_CHOICES = [
        ("",                           "Select level"),
        ("Internship",                 "Internship"),
        ("Entry Level (0–2 yrs)",      "Entry Level (0–2 yrs)"),
        ("Mid Level (2–5 yrs)",        "Mid Level (2–5 yrs)"),
        ("Senior Level (5–10 yrs)",    "Senior Level (5–10 yrs)"),
        ("Lead / Manager",             "Lead / Manager"),
        ("Executive / Director",       "Executive / Director"),
    ]
    WORK_MODE_CHOICES = [
        ("",         "Select mode"),
        ("On-site",  "On-site"),
        ("Remote",   "Remote"),
        ("Hybrid",   "Hybrid"),
    ]
    EDUCATION_CHOICES = [
        ("",                        "Select education"),
        ("High School / Matric",    "High School / Matric"),
        ("Intermediate (FA/FSc)",   "Intermediate (FA/FSc)"),
        ("Bachelor's Degree",       "Bachelor's Degree"),
        ("Master's Degree",         "Master's Degree"),
        ("PhD / Doctorate",         "PhD / Doctorate"),
        ("No Requirement",          "No Requirement"),
    ]
    YEARS_EXP_CHOICES = [
        ("",                      "Select years"),
        ("No experience needed",  "No experience needed"),
        ("Less than 1 year",      "Less than 1 year"),
        ("1–2 years",             "1–2 years"),
        ("2–4 years",             "2–4 years"),
        ("4–6 years",             "4–6 years"),
        ("6–10 years",            "6–10 years"),
        ("10+ years",             "10+ years"),
    ]
    SALARY_TYPE_CHOICES = [
        ("range",      "Salary Range"),
        ("fixed",      "Fixed Amount"),
        ("negotiable", "Negotiable"),
        ("unpaid",     "Unpaid (Internship)"),
    ]
    CURRENCY_CHOICES = [
        ("PKR", "PKR – Pakistani Rupee"),
        ("USD", "USD – US Dollar"),
        ("EUR", "EUR – Euro"),
        ("GBP", "GBP – British Pound"),
        ("AED", "AED – UAE Dirham"),
        ("SAR", "SAR – Saudi Riyal"),
    ]
    VISIBILITY_CHOICES = [
        ("public",  "Public"),
        ("private", "Private"),
    ]

    category          = forms.ChoiceField(choices=CATEGORY_CHOICES,   widget=forms.Select(attrs={"id": "jobCategory"}))
    experience_level  = forms.ChoiceField(choices=EXP_CHOICES,        widget=forms.Select(attrs={"id": "expLevel"}))
    work_mode         = forms.ChoiceField(choices=WORK_MODE_CHOICES,   widget=forms.Select(attrs={"id": "workMode"}))
    minimum_education = forms.ChoiceField(choices=EDUCATION_CHOICES,   widget=forms.Select(attrs={"id": "education"}), required=False)
    years_of_experience= forms.ChoiceField(choices=YEARS_EXP_CHOICES, widget=forms.Select(attrs={"id": "yearsExp"}), required=False)
    salary_type       = forms.ChoiceField(choices=SALARY_TYPE_CHOICES, widget=forms.Select(attrs={"id": "salaryType", "onchange": "toggleSalary()"}))
    currency          = forms.ChoiceField(choices=CURRENCY_CHOICES,    widget=forms.Select(attrs={"id": "currency"}))
    visibility        = forms.ChoiceField(choices=VISIBILITY_CHOICES,  widget=forms.RadioSelect(), initial="public")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            active_categories = JobCategory.objects.filter(is_active=True).values_list('name', 'name')
            self.fields['category'].choices = [('', 'Select category')] + list(active_categories)
        except Exception:
            pass

    def clean_vacancies(self):
        v = self.cleaned_data.get("vacancies", 1)
        return max(1, int(v)) if v else 1

    def clean_skills(self):
        """Ensure skills is clean comma-separated string."""
        raw = self.cleaned_data.get("skills", "")
        parts = [s.strip() for s in raw.split(",") if s.strip()]
        return ",".join(parts)

    def clean_perks(self):
        """Ensure perks is clean comma-separated string."""
        raw = self.cleaned_data.get("perks", "")
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        return ",".join(parts)

    def clean(self):
        cleaned = super().clean()
        salary_type = cleaned.get("salary_type")

        if salary_type == "range":
            if not cleaned.get("salary_min") and not cleaned.get("salary_max"):
                pass  # optional — allow empty range
        return cleaned

# ─────────────────────────────────────────────────────────
#  NEW: SETTINGS FORMS
# ─────────────────────────────────────────────────────────
class CompanyUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'owner@example.com'}),
        }

class CompanyProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        # Adapt these fields to match your exact CompanyProfile model columns
        fields = [
            'trade_name', 'legal_name', 'ntn_number', 'company_email',
            'company_phone', 'landline', 'website', 'company_type',
            'industry', 'country', 'province', 'city', 'legal_address',
            'overview', 'logo'
        ]
        widgets = {
            'trade_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter trade name'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter legal name'}),
            'ntn_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter NTN/CUIN'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@company.com'}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 1234567'}),
            'landline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+92 21 12345678'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.company.com'}),
            'company_type': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state or province'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'legal_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter complete address'}),
            'overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your company'}),
            'logo': forms.FileInput(attrs={'class': 'd-none', 'id': 'logoUpload', 'onchange': 'previewMyLogo(this)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            active_types = CompanyType.objects.filter(is_active=True).values_list('name', 'name')
            self.fields['company_type'].widget.choices = [('', 'Select type')] + list(active_types)
        except Exception:
            self.fields['company_type'].widget.choices = [('', 'Select type')]