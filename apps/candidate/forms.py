from django import forms
from .models import (
    CandidateProfile, ProfessionalInfo, LocationInfo,
    AboutMe, Resume, Skill, Education, WorkExperience,
    SocialLinks, CandidateCertification
)
import re

class RequiredFieldsMixin:
    required_fields = []

    def clean(self):
        cleaned_data = super().clean()
        for field in self.required_fields:
            value = cleaned_data.get(field)
            if not value:
                label = self.fields[field].label or field
                self.add_error(field, f"{label} fill karna zaruri hai!")
        return cleaned_data


class CandidateProfileForm(RequiredFieldsMixin, forms.ModelForm):
    required_fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
    class Meta:
        model = CandidateProfile
        fields = [
            'first_name', 'last_name', 'username', 'phone_number',
            'email', 'date_of_birth', 'gender', 'cnic_number',
            'profile_photo', 'id_card_front', 'id_card_back'
        ]

    def clean_cnic_number(self):
        cnic = self.cleaned_data.get('cnic_number')
        # 35202-1234567-1 format enforce
        if cnic and not re.match(r'^\d{5}-\d{7}-\d{1}$', cnic):
            raise forms.ValidationError("CNIC format: 35202-1234567-1")
        return cnic

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not re.match(r'^03\d{9}$', phone):
            raise forms.ValidationError("Phone: 03XXXXXXXXX format mein hona chahiye")
        return phone


class ProfessionalInfoForm(RequiredFieldsMixin, forms.ModelForm):
    required_fields = ['job_title', 'industry']
    class Meta:
        model = ProfessionalInfo
        fields = ['job_title', 'industry', 'years_of_experience',
                  'job_type_preference', 'availability']


class LocationInfoForm(RequiredFieldsMixin, forms.ModelForm):
    required_fields = ['province', 'city']
    class Meta:
        model = LocationInfo
        fields = ['province', 'city', 'postal_code', 'full_address']


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = AboutMe
        fields = ['professional_summary', 'career_objective']


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Sirf PDF/DOCX allow karo
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx']:
                raise forms.ValidationError("Sirf PDF ya DOCX allowed hai.")
            # Max 5MB
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File 5MB se bari nahi honi chahiye.")
        return file


class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = SocialLinks
        fields = ['github', 'twitter_x', 'linkedin', 'portfolio']


class EducationForm(RequiredFieldsMixin, forms.ModelForm):
    required_fields = ['degree', 'institution_name', 'start_year']
    class Meta:
        model = Education
        fields = ['degree', 'institution_name', 'field_of_study',
                  'start_year', 'end_year', 'grade_cgpa']

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_year')
        end = cleaned.get('end_year')
        if start and end and end < start:
            raise forms.ValidationError("End year start year se pehle nahi ho sakta.")
        return cleaned


class WorkExperienceForm(RequiredFieldsMixin, forms.ModelForm):
    required_fields = ['job_title', 'company_name', 'start_date'] 
    class Meta:
        model = WorkExperience
        fields = ['job_title', 'company_name', 'start_date',
                  'end_date', 'employment_type', 'achievements']

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("End date start date se pehle nahi ho sakti.")
        return cleaned


class CertificationForm(forms.ModelForm):
    class Meta:
        model = CandidateCertification
        fields = ['name', 'issuing_organization', 'issue_date',
                  'expiration_date', 'credential_id', 'credential_url']