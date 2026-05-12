from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


# ─────────────────────────────────────────
#  Admin Login Form
# ─────────────────────────────────────────
class AdminLoginForm(forms.Form):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class":       "form-control",
            "placeholder": "admin@jobhive.com",
            "autofocus":   True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class":       "form-control",
            "placeholder": "••••••••",
            "id":          "adminPass",
        }),
    )

    def clean(self):
        cleaned = super().clean()
        email    = cleaned.get("username")
        password = cleaned.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_staff:
                raise forms.ValidationError("You do not have admin access.")
            cleaned["user"] = user
        return cleaned


# ─────────────────────────────────────────
#  Admin Forgot Password Form
# ─────────────────────────────────────────
class AdminForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class":       "form-control",
            "placeholder": "admin@jobhive.com",
        }),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email, is_staff=True).exists():
            raise forms.ValidationError("No admin account found with this email.")
        return email


# ─────────────────────────────────────────
#  Admin Reset Password Form
# ─────────────────────────────────────────
class AdminResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class":       "form-control",
            "placeholder": "Create a strong password",
            "id":          "newPass",
        }),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class":       "form-control",
            "placeholder": "Re-enter your password",
            "id":          "confirmPass",
        }),
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned