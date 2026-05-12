from django.shortcuts        import render, redirect
from django.contrib.auth     import login, logout, get_user_model
from django.contrib          import messages
from django.utils.http       import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding   import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail        import send_mail
from django.conf             import settings
from django.urls             import reverse

from .forms      import AdminLoginForm, AdminForgotPasswordForm, AdminResetPasswordForm
from .decorators import admin_login_required

User = get_user_model()


# ─────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────
def admin_login(request):
    # Har baar login page aane par pehle logout
    if request.user.is_authenticated:
        logout(request)

    form = AdminLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]
        login(request, user)
        messages.success(request, f"Welcome back, {user.email}!")
        return redirect("custom_admin:dashboard")

    return render(request, "custom_admin/admin_login.html", {"form": form})


# ─────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────
@admin_login_required
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("custom_admin:login")


# ─────────────────────────────────────────
#  FORGOT PASSWORD
# ─────────────────────────────────────────
def admin_forgot_password(request):
    form = AdminForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user  = User.objects.get(email=email, is_staff=True)

        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # reverse() khud urls.py ka prefix read karta hai
        # agar urls.py mein path('admin/', ...) hai
        # to yeh automatically localhost:8000/admin/reset-password/... banega
        reset_path = reverse("custom_admin:reset_password", kwargs={
            "uidb64": uid,
            "token":  token,
        })
        reset_url = f"{request.scheme}://{request.get_host()}{reset_path}"

        send_mail(
            subject = "JobHive Admin — Password Reset",
            message = (
                f"Hello {user.email},\n\n"
                f"Click the link below to reset your admin password:\n\n"
                f"{reset_url}\n\n"
                f"This link expires in 24 hours.\n\n"
                f"If you did not request this, ignore this email.\n\n"
                f"— JobHive Admin Team"
            ),
            from_email     = settings.EMAIL_HOST_USER,
            recipient_list = [email],
            fail_silently  = False,
        )

        messages.success(request, "Password reset link has been sent to your email address.")
        return redirect("custom_admin:forgot_password")

    return render(request, "custom_admin/admin_forgot_password.html", {"form": form})


# ─────────────────────────────────────────
#  RESET PASSWORD
# ─────────────────────────────────────────
def admin_reset_password(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, is_staff=True)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "custom_admin/admin_reset_invalid.html")

    form = AdminResetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        messages.success(request, "Password has been reset successfully. Please log in.")
        return redirect("custom_admin:login")

    return render(request, "custom_admin/admin_reset_password.html", {
        "form":   form,
        "uidb64": uidb64,
        "token":  token,
    })


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────
@admin_login_required
def admin_dashboard(request):
    total_users      = User.objects.count()
    total_candidates = User.objects.filter(role="CANDIDATE").count() if hasattr(User, "role") else 0
    total_companies  = User.objects.filter(role="COMPANY").count()   if hasattr(User, "role") else 0
    total_admins     = User.objects.filter(is_staff=True).count()

    recent_users = User.objects.order_by("-date_joined")[:10]

    context = {
        "total_users":      total_users,
        "total_candidates": total_candidates,
        "total_companies":  total_companies,
        "total_admins":     total_admins,
        "recent_users":     recent_users,
        "admin_user":       request.user,
    }
    return render(request, "custom_admin/admin_dashboard.html", context)