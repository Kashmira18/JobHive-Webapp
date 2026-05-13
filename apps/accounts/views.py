from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser
from .forms import (
    CustomUserRegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
)


# ── REGISTER ──
def register_view(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == "COMPANY":
                messages.success(
                    request, "Registration successful! Please wait for admin approval."
                )
                return redirect("login")
            else:
                login(request, user)
                return redirect("candidate_dashboard")
        # agar form invalid ho, errors show hone dain
    else:
        form = CustomUserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# ── LOGIN ──
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if "@" in username:
            try:
                # user_obj = CustomUser.objects.get(email=username)
                user_obj = CustomUser.objects.filter(email=username).first()
                # Agar mil jaye, toh uska asli 'username' nikaal lein
                target_username = user_obj.username
            except CustomUser.DoesNotExist:
                target_username = None
        else:
            # Agar email nahi hai, toh input ko hi username samjhein
            target_username = username


        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            login(request, user)
            if user.role == "COMPANY":
                if not user.is_approved:
                    logout(request)
                    messages.error(request, "Your company account is not approved yet.")
                    return redirect("login")
                return redirect("company_dashboard")
            else:
                return redirect("candidate_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")


# ── LOGOUT ──
def logout_view(request):
    logout(request)
    return redirect("login")


# ── FORGOT PASSWORD ──
def custom_forget_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        users = CustomUser.objects.filter(email=email)

        if users.exists():
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = f"{request.scheme}://{request.get_host()}/auth/reset-password/{uid}/{token}/"

                subject = "Reset Your JobHive Password"
                email_template = "accounts/email/forget_password_email.html"
                parameters = {"user": user, "reset_url": reset_url}
                msg_html = render_to_string(email_template, parameters)

                send_mail(
                    subject,
                    "Please reset your password using the link provided.",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    html_message=msg_html,
                    fail_silently=False,
                )
            messages.success(request, "Password reset link sent to your email.")
            return redirect("login")
        else:
            messages.error(request, "No account found with this email address.")
    return render(request, "accounts/forget_password.html")


# ── RESET PASSWORD CONFIRM ──
def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                messages.success(
                    request, "Password reset successful! Login with your new password."
                )
                return redirect("login")
            else:
                for error in form.errors.values():
                    messages.error(request, error.as_text())
        else:
            form = SetNewPasswordForm()
        return render(request, "accounts/password_reset_confirm.html", {"form": form})
    else:
        return render(request, "accounts/password_reset_invalid.html")


def custom_password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def custom_password_reset_invalid(request):
    return render(request, 'accounts/password_reset_invalid.html')