from django import forms

class JobApplicationForm(forms.Form):
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Write something about yourself...',
            'rows': 6,
            'class': 'form-control',
        }),
        required=False
    )
    
    resume_snapshot = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.doc,.docx',
            'class': 'form-control',
        }),
        required=False
    )
    
    def clean_resume_snapshot(self):
        resume = self.cleaned_data.get('resume_snapshot')
        
        if resume:
            # Check file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            
            if resume.content_type not in allowed_types:
                raise forms.ValidationError("Only PDF or DOCX files are allowed")
            
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024
            if resume.size > max_size:
                raise forms.ValidationError(f"File too large. Max 5MB, yours is {resume.size / 1024 / 1024:.2f}MB")
        
        return resume