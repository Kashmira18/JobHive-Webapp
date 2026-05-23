from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from company.models import CompanyType

from .forms import AdminLoginForm, AdminForgotPasswordForm, AdminResetPasswordForm
from .decorators import admin_login_required
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import CompanyProfile, CustomUser

User = get_user_model()


# ─────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────


def admin_login(request):
    form = AdminLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]

        # AUTO ADMIN CHECK
        if user.is_superuser:
            # login(request, user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("custom_admin:admin_dashboard")
        else:
            form.add_error(None, "You are not authorized as admin")
    # else:
    #     form.add_error(None, "Invalid Admin credentials.")
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
        user = User.objects.get(email=email, is_staff=True)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # reverse() khud urls.py ka prefix read karta hai
        # agar urls.py mein path('admin/', ...) hai
        # to yeh automatically localhost:8000/admin/reset-password/... banega
        reset_path = reverse(
            "custom_admin:reset_password",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )
        reset_url = f"{request.scheme}://{request.get_host()}{reset_path}"

        send_mail(
            subject="JobHive Admin — Password Reset",
            message=(
                f"Hello {user.email},\n\n"
                f"Click the link below to reset your admin password:\n\n"
                f"{reset_url}\n\n"
                f"This link expires in 24 hours.\n\n"
                f"If you did not request this, ignore this email.\n\n"
                f"— JobHive Admin Team"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(
            request, "Password reset link has been sent to your email address."
        )
        return redirect("custom_admin:forgot_password")

    return render(request, "custom_admin/admin_forgot_password.html", {"form": form})


# ─────────────────────────────────────────
#  RESET PASSWORD
# ─────────────────────────────────────────
def admin_reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, is_staff=True)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "custom_admin/admin_reset_invalid.html")

    form = AdminResetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        messages.success(
            request, "Password has been reset successfully. Please log in."
        )
        return redirect("custom_admin:login")

    return render(
        request,
        "custom_admin/admin_reset_password.html",
        {
            "form": form,
            "uidb64": uidb64,
            "token": token,
        },
    )

# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────
@admin_login_required
def admin_dashboard(request):
    # Stats
    total_users = User.objects.count()
    total_candidates = User.objects.filter(role="CANDIDATE").count()
    total_companies = User.objects.filter(role="COMPANY").count()
    total_admins = User.objects.filter(is_staff=True).count()

    # Companies by status
    pending_companies = User.objects.filter(role="COMPANY", company_profile__company_status="PENDING").select_related("company_profile")

    approved_companies = User.objects.filter(role="COMPANY", company_profile__company_status="APPROVED").select_related("company_profile")
    rejected_companies = User.objects.filter(role="COMPANY", company_profile__company_status="REJECTED").select_related("company_profile")
    rollback_companies = User.objects.filter(role="COMPANY", company_profile__company_status="ROLLBACK").select_related("company_profile")

    # Recent registrations
    recent_users = User.objects.order_by("-date_joined")[:10]

    context = {
        "total_users": total_users,
        "total_candidates": total_candidates,
        "total_companies": total_companies,
        "total_admins": total_admins,
        "pending_companies": pending_companies,
        "approved_companies": approved_companies,
        "rejected_companies": rejected_companies,
        "rollback_companies": rollback_companies,
        "recent_users": recent_users,
        "admin_user": request.user,
    }
    return render(request, "custom_admin/admin_dashboard.html", context)


# ──────────────────────────────────────────────
#  COMPANY DETAIL VIEW
# ──────────────────────────────────────────────
@admin_login_required
def view_company_details(request, user_id):
    company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
    try:
        profile = company_user.company_profile
    except CompanyProfile.DoesNotExist:
        profile = None

    context = {
        "company_user": company_user,
        "profile": profile,
    }
    return render(request, "custom_admin/view_company_details.html", context)

# _____________________________________________________________________________________________________________________________
# # ────────────────────────────────────────────
# #  APPROVE COMPANY
# # ──────────────────────────────────────────────
# @admin_login_required
# def approve_company(request, user_id):
#     company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

#     try:
#         profile = company_user.company_profile
#     except CompanyProfile.DoesNotExist:
#         profile = None

#     # POST — approve karo
#     if request.method == "POST":
#         company_user.is_approved = True
#         company_user.save()

#         if profile:
#             profile.company_status = "APPROVED"
#             profile.feedback = ""
#             profile.rejected_fields = {}
#             profile.save()

#         messages.success(request, f"{company_user.email} approved successfully.")
#         return redirect("custom_admin:admin_dashboard")

#     # GET — confirmation page dikhao
#     return render(request, "custom_admin/approve_company.html", {
#         "company_user": company_user,
#         "profile": profile,
#     })
# # def approve_company(request, user_id):
#     company = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
#     company.is_approved = True
#     company.company_status = "APPROVED"
#     company.save()

#     try:
#         profile = company.company_profile
#         profile.feedback = ""
#         profile.save()
#     except CompanyProfile.DoesNotExist:
#         messages.error(request,'Compny not found.')

#     messages.success(request, f"{company.email} approved successfully.")
#     return redirect("custom_admin:admin_dashboard")


# # ──────────────────────────────────────────────
# #  REJECT COMPANY
# #  Company ko login hi nahi karne deta
# # ──────────────────────────────────────────────
# @admin_login_required
# def reject_company(request, user_id):
#     company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

#     if request.method == "POST":
#         try:
#             profile = company_user.company_profile
#         except CompanyProfile.DoesNotExist:
#             profile = CompanyProfile.objects.create(user=company_user)

#         profile.admin_message = request.POST.get("admin_message", "").strip()
#         profile.rejection_reason = profile.admin_message

#         # Build rejected_fields from checkboxes + reasons
#         rejected = {}
#         field_keys = [
#             "trade_name",
#             "legal_name",
#             "ntn_number",
#             "company_email",
#             "company_type",
#             "industry",
#             "logo",
#             "city",
#             "legal_address",
#             "country",
#             "province",
#             "website",
#             "overview",
#         ]
#         for key in field_keys:
#             reason = request.POST.get(f"field_{key}", "").strip()
#             if reason:
#                 rejected[key] = reason

#         profile.rejected_fields = rejected
#         profile.save()

#         company_user.is_approved = False
#         company_user.company_status = "REJECTED"
#         company_user.save()

#         messages.success(request, f"{company_user.email} rejected.")

#         return redirect('custom_admin:admin_dashboard')
#         # return render("custom_admin/reject_company.html")
#         # return render(request, "custom_admin/reject_company.html")

#     # GET — show reject form
#     try:
#         profile = company_user.company_profile
#     except CompanyProfile.DoesNotExist:
#         profile = None

#     return render(request,"custom_admin/reject_company.html",{"company_user": company_user, "profile": profile})


# # ──────────────────────────────────────────────
# #  ROLLBACK COMPANY
# #  Company login kar sakti hai, form fill karke
# #  resubmit kar sakti hai specific fields
# # ──────────────────────────────────────────────
# @admin_login_required
# def rollback_company(request, user_id):
#     company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

#     if request.method == "POST":
#         try:
#             profile = company_user.company_profile
#         except CompanyProfile.DoesNotExist:
#             profile = CompanyProfile.objects.create(user=company_user)

#         profile.admin_message = request.POST.get("admin_message", "").strip()

#         # Build rollback fields 
#         rollback_fields = {}
#         field_keys = [
#             "trade_name",
#             "legal_name",
#             "ntn_number",
#             "company_email",
#             "company_type",
#             "industry",
#             "logo",
#             "city",
#             "legal_address",
#             "country",
#             "province",
#             "website",
#             "overview",
#         ]
#         for key in field_keys:
#             reason = request.POST.get(f"field_{key}", "").strip()
#             if reason:
#                 rollback_fields[key] = reason

#         profile.rejected_fields = rollback_fields
#         profile.save()

#         company_user.is_approved = False
#         company_user.company_status = "ROLLBACK"
#         company_user.save()

#         messages.success(request, f"{company_user.email} sent for rollback correction.")
#         return redirect("custom_admin:admin_dashboard")

#     # show rollback form
#     try:
#         profile = company_user.company_profile
#     except CompanyProfile.DoesNotExist:
#         profile = None

#     return render(
#         request,
#         "custom_admin/rollback_company.html",
#         {
#             "company_user": company_user,
#             "profile": profile,
#         },
#     )
# _____________________________________________________________________________________________________________________________


@admin_login_required
def approve_company(request, user_id):
    company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

    # ── CustomUser pe dono fields update karo ──
    company_user.is_approved    = True
    # company_user.company_status = "APPROVED"   
    company_user.save()

    # ── Profile ka rejection data clear karo ──
    try:
        profile = company_user.company_profile
        profile.company_status = "JUST_APPROVED"
        profile.rejected_fields  = {}
        profile.rejection_reason = ""
        profile.admin_message    = ""
        profile.save()
    except Exception:
        pass

    messages.success(request, f"{company_user.email} approved successfully.")
    return redirect("custom_admin:admin_dashboard")   


@admin_login_required
def reject_company(request, user_id):
    company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

    if request.method == "POST":
        try:
            profile = company_user.company_profile
        except CompanyProfile.DoesNotExist:
            profile = CompanyProfile.objects.create(user=company_user)

        profile.admin_message    = request.POST.get("admin_message", "").strip()
        profile.rejection_reason = profile.admin_message
        profile.company_status = "REJECTED"

        rejected = {}
        field_keys = [
            "trade_name", "legal_name", "ntn_number", "company_email",
            "company_type", "industry", "logo", "city",
            "legal_address", "country", "province", "website", "overview",
        ]
        for key in field_keys:
            reason = request.POST.get(f"field_{key}", "").strip()
            if reason:
                rejected[key] = reason

        profile.rejected_fields = rejected
        profile.save()

        company_user.is_approved    = False
        company_user.company_status = "REJECTED"
        company_user.save()

        messages.success(request, f"{company_user.email} rejected.")
        return redirect("custom_admin:admin_dashboard")

    try:
        profile = company_user.company_profile
    except CompanyProfile.DoesNotExist:
        profile = None

    return render(request, "custom_admin/reject_company.html", {
        "company_user": company_user,
        "profile":      profile,
    })


@admin_login_required
def rollback_company(request, user_id):
    company_user = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")

    if request.method == "POST":
        try:
            profile = company_user.company_profile
        except CompanyProfile.DoesNotExist:
            profile = CompanyProfile.objects.create(user=company_user)

        profile.admin_message = request.POST.get("admin_message", "").strip()
        profile.company_status = "ROLLBACK"

        rollback_fields = {}
        field_keys = [
            "trade_name", "legal_name", "ntn_number", "company_email",
            "company_type", "industry", "logo", "city",
            "legal_address", "country", "province", "website", "overview",
        ]
        for key in field_keys:
            reason = request.POST.get(f"field_{key}", "").strip()
            if reason:
                rollback_fields[key] = reason

        profile.rejected_fields = rollback_fields
        profile.save()

        company_user.is_approved    = False
        company_user.company_status = "ROLLBACK"
        company_user.save()

        messages.success(request, f"{company_user.email} sent for rollback.")
        return redirect("custom_admin:admin_dashboard")

    try:
        profile = company_user.company_profile
    except CompanyProfile.DoesNotExist:
        profile = None

    return render(request, "custom_admin/rollback_company.html", {
        "company_user": company_user,
        "profile":      profile,
    })
















# ________________________________________
def admin_layout(request):
    return render(request, "custom_admin/admin_layout.html")


def company_type(request):
    return render(request, "custom_admin/company_type.html")


# # @admin_login_required 
# def admin_company_list(request):
#     companies = CustomUser.objects.filter(role="COMPANY")
#     return render(request, "custom_admin/admin_dashboard.html", {"companies": companies})
def admin_company_list(request):
    companies = CustomUser.objects.filter(role="COMPANY")
    # Ya jo bhi aapka related model name ho: 'profile', 'company', etc.
    
    return redirect("custom_admin:admin_dashboard")

# @admin_login_required 
# def approve_company(request, user_id):
#     company = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
#     company.is_approved = True
#     company.save()
#     return redirect("custom_admin:admin_company_list")


# @admin_login_required 
# def reject_company(request, user_id):
#     company = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
#     company.is_approved = False
#     company.save()
#     return redirect("custom_admin:admin_company_list")


# def company_type_list(request):
#     types = CompanyType.objects.all()
#     return render(request, "custom_admin/company_type.html", {"types": types})


# def delete_company(request, user_id):
#     company = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
#     company.delete()
#     return redirect("custom_admin:admin_dashboard")

# def edit_company(request, user_id):
#     company = get_object_or_404(CustomUser, pk=user_id, role="COMPANY")
#     # Implement form handling for editing company details
#     return render(request, "custom_admin/edit_company.html", {"company": company})