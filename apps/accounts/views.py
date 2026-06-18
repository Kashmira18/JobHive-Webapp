from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser, CompanyProfile, CompanyRejection
from .forms import (
    CustomUserRegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
)
# companyRejection model ko import karna hai taake company resubmit page mein rejected fields dikha sakein


# ── REGISTER ──
def register_view(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            if user.role == "COMPANY":
                # Company → pending
                # user session mein store hoa sirf pending show karne ke liye

                request.session["pending_user_id"] = user.pk
                # messages.success(
                #     request, "Registration successful! Please wait for admin approval."
                # )
                # return redirect("login")
                return redirect("company_registration")
            else:
                # login(request, user)
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                messages.success(request, f"Welcome to JobHive, {user.username}!")
                return redirect("candidate_dashboard")
    else:
        form = CustomUserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# ── LOGIN ──

# _______________________________________________________________________________________


# def login_view(request):
#     if request.method == "POST":
#         username_or_email = request.POST.get("username", "").strip()
#         password = request.POST.get("password", "")

#         # Email se username nikalna
#         if "@" in username_or_email:
#             user_obj = CustomUser.objects.filter(
#                 email__iexact=username_or_email
#             ).first()
#             target_username = user_obj.username if user_obj else None
#         else:
#             target_username = username_or_email

#         user = authenticate(request, username=target_username, password=password)

#         if user is not None:

#             # ── COMPANY ──
#             if user.role == "COMPANY":

#                 if user.is_approved:
#                     # Approved → pehle congrats page, login wahan hoga
#                     request.session["pending_user_id"] = user.pk
#                     return redirect("company_approved")  # ← CHANGE
#                 else:
#                     # Not approved → pending page
#                     request.session["pending_user_id"] = user.pk
#                     return redirect("company_pending")

#             # ── CANDIDATE ──
#             else:
#                 login(request, user)
#                 return redirect("candidate:candidate_dashboard")

#         else:
#             messages.error(
#                 request, "Invalid email/username or password. Please try again."
#             )

#     return render(request, "accounts/login.html")

# _______________________________________________________________________________



def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password          = request.POST.get("password", "")

        if "@" in username_or_email:
            user_obj        = CustomUser.objects.filter(email__iexact=username_or_email).first()
            target_username = user_obj.username if user_obj else None
        else:
            target_username = username_or_email

        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            if user.role == "COMPANY":
                request.session["pending_user_id"] = user.pk

                # ── company_status CompanyProfile mein hai ──
                try:
                    status = user.company_profile.company_status or "PENDING"
                except CompanyProfile.DoesNotExist:
                    status = "PENDING"

                # ── APPROVED ──
                if user.is_approved and status == "APPROVED":
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                    return redirect("company:company_dashboard")

                # ── REJECTED → resubmit form ──
                elif status == "REJECTED":
                    return redirect("company_resubmit")

                # ── ROLLBACK → resubmit form ──
                elif status == "ROLLBACK":
                    return redirect("company_resubmit")

                # ── PENDING ya kuch aur ──
                else:
                    return redirect("company_pending")

            else:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("candidate:candidate_dashboard")

        else:
            messages.error(request, "Invalid email/username or password. Please try again.")

    return render(request, "accounts/login.html", {"form": form})

# def login_view(request):
#     form = LoginForm(request.POST or None)

#     if request.method == "POST":
#         username_or_email = request.POST.get("username", "").strip()
#         password          = request.POST.get("password", "")

#         if "@" in username_or_email:
#             user_obj        = CustomUser.objects.filter(email__iexact=username_or_email).first()
#             target_username = user_obj.username if user_obj else None
#         else:
#             target_username = username_or_email

#         user = authenticate(request, username=target_username, password=password)

#         if user is not None:
#             if user.role == "COMPANY":
#                 request.session["pending_user_id"] = user.pk

#                 # Profile se safe tareeqay se status check karna
#                 try:
#                     profile = user.company_profile
#                     status = profile.company_status
#                 except CompanyProfile.DoesNotExist:
#                     status = "PENDING"

#                 # ── APPROVED ──
#                 if user.is_approved and status == "APPROVED":
#                     login(request, user, backend="django.contrib.auth.backends.ModelBackend")
#                     return redirect("company:company_dashboard")

#                 elif user.is_approved and status == "JUST_APPROVED":
#                     request.session["pending_user_id"] = user.pk
#                     return redirect("company_approved")

#                 # ── REJECTED ──
#                 elif status == "REJECTED":
#                     return redirect("company_resubmit")

#                 # ── ROLLBACK ──
#                 elif status == "ROLLBACK":
#                     return redirect("company_resubmit")

#                 # ── PENDING ──
#                 else:
#                     return redirect("company_pending")

#             else:
#                 # Candidate logic
#                 login(request, user, backend="django.contrib.auth.backends.ModelBackend")
#                 return redirect("candidate:candidate_dashboard")

#         else:
#             messages.error(request, "Invalid email/username or password. Please try again.")

#     return render(request, "accounts/login.html", {"form": form})




def company_approved(request):
    user_id = request.session.get("pending_user_id")

    if not user_id:
        if request.user.is_authenticated and request.user.role == "COMPANY":
            return redirect("company:company_dashboard")
        return redirect("login")

    try:
        user = CustomUser.objects.get(pk=user_id)
        profile = user.company_profile
    except (CustomUser.DoesNotExist, CompanyProfile.DoesNotExist):
        return redirect("login")

    if not user.is_approved:
        return redirect("company_pending")

    # ── STATUS CHANGED TO PERMANENT APPROVED ──
    # Taake agli dafa login karne par Congrats page bypass ho jaye
    profile.company_status = "APPROVED"
    profile.save()

    # Session clear
    if "pending_user_id" in request.session:
        del request.session["pending_user_id"]

    # Login execute karein
    login(request, user, backend="django.contrib.auth.backends.EmailOrUsernameBackend")

    # Congrats template render hoga jahan 5 sec ka JS laga hai
    return render(request, "accounts/company_approved.html", {"user": user})







# ── LOGOUT ──
def logout_view(request):
    request.session.flush()  # session clear
    logout(request)
    return redirect("login")


#  ── COMPANY — PENDING PAGE ──
#  (After registration , login with pending status)
def company_pending(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return redirect("login")

    # when approved ->  show approved page
    if user.is_approved:
        return redirect("company_approved")

    return render(request, "accounts/company_pending.html", {"user": user})


# ── COMPANY — DOCUMENTS REVIEW PAGE ──
def company_documents_review(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return redirect("login")

    if request.method == "POST":

        messages.success(
            request, "Documents uploaded successfully. We will review them shortly."
        )
        return redirect("company_pending")

    approved_docs = [
        # {'name': 'Business Registration Certificate', 'id': 1},
    ]
    rejected_docs = [
        # {'name': 'NTN Certificate', 'id': 2, 'status': 'Rejected', 'reason': 'Document is blurry or unreadable.'},
        # {'name': 'CNIC Copy', 'id': 3, 'status': 'Missing', 'reason': 'This document was not submitted.'},
    ]

    context = {
        "user": user,
        "approved_docs": approved_docs,
        "rejected_docs": rejected_docs,
    }
    return render(request, "accounts/company_documents_review.html", context)


# __________________________________________
# def company_approved(request):

#     # Session --> user
#     user_id = request.session.get('pending_user_id')

#     if not user_id:
#         messages.error(request, "Session expired. Please login again.")
#         return redirect("login")

#     try:
#         user = CustomUser.objects.get(pk=user_id)
#     except CustomUser.DoesNotExist:
#         messages.error(request, "User not found. Please login again.")
#         return redirect("login")

#     # Agar approved nahi hai then
#     if not user.is_approved:
#         return redirect("company_pending")

#     # Session clear karo
#     del request.session['pending_user_id']

#     return render(request, "accounts/company_approved.html", {"user": user})
# __________________________________________


def company_approved(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")
    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return redirect("login")
    if not user.is_approved:
        return redirect("company_pending")

    # Session clear karo
    del request.session["pending_user_id"]

    # Ab login karo
    # login(request, user)
    login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')


    return render(request, "accounts/company_approved.html", {"user": user})


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
    return render(request, "accounts/password_reset_done.html")


def custom_password_reset_invalid(request):
    return render(request, "accounts/password_reset_invalid.html")


def company_registration(request):
    # Session se user lo
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    try:
        user = CustomUser.objects.get(pk=user_id, role="COMPANY")
    except CustomUser.DoesNotExist:
        return redirect("login")

    # Already approved hai to dashboard pe bhejo
    if user.is_approved:
        return redirect("company_dashboard")

    # GET — form dikhao
    if request.method == "GET":
        return render(request, "accounts/company_registration.html", {"user": user})

    # POST — form process karo
    # ── User fields update ──
    user.first_name = request.POST.get("first_name", "").strip()
    user.last_name = request.POST.get("last_name", "").strip()
    user.phone = request.POST.get("owner_phone", "").strip()

    # ── CompanyProfile get or create ──
    profile, _ = CompanyProfile.objects.get_or_create(user=user)

    profile.designation = request.POST.get("designation", "").strip()
    profile.trade_name = request.POST.get("trade_name", "").strip()
    profile.legal_name = request.POST.get("legal_name", "").strip()
    profile.ntn_number = request.POST.get("ntn_number", "").strip()
    profile.company_email = request.POST.get("company_email", "").strip()
    profile.company_type = request.POST.get("company_type", "").strip()
    profile.industry = request.POST.get("industry", "").strip()
    profile.total_employees = request.POST.get("total_employees", "").strip()
    profile.landline = request.POST.get("landline", "").strip()
    profile.company_phone = request.POST.get("company_phone", "").strip()
    profile.website = request.POST.get("website", "").strip()
    profile.country = request.POST.get("country", "").strip()
    profile.province = request.POST.get("province", "").strip()
    profile.city = request.POST.get("city", "").strip()
    profile.postal_code = request.POST.get("postal_code", "").strip()
    profile.legal_address = request.POST.get("legal_address", "").strip()
    profile.overview = request.POST.get("overview", "").strip()
    profile.vision = request.POST.get("vision", "").strip()
    profile.facebook = request.POST.get("facebook", "").strip()
    profile.twitter = request.POST.get("twitter", "").strip()
    profile.linkedin = request.POST.get("linkedin", "").strip()
    profile.pinterest = request.POST.get("pinterest", "").strip()

    # est_date — empty string se error aata hai
    est_date = request.POST.get("est_date", "").strip()
    profile.est_date = est_date if est_date else None

    # Logo upload
    if "logo" in request.FILES:
        profile.logo = request.FILES["logo"]

    # ── Validation ──
    errors = []
    if not profile.trade_name:
        errors.append("Company Trade Name is required.")
    if not profile.legal_name:
        errors.append("Company Legal Name is required.")
    if not profile.company_type:
        errors.append("Company Type is required.")
    if not profile.industry:
        errors.append("Industry is required.")
    if not profile.country:
        errors.append("Country is required.")
    if not profile.city:
        errors.append("City is required.")
    if not profile.legal_address:
        errors.append("Legal Address is required.")

    if errors:
        for err in errors:
            messages.error(request, err)
        return render(request, "accounts/company_registration.html", {"user": user})

    # ── Save ──
    user.save()
    profile.save()

    messages.success(
        request, "Company profile submitted! Please wait for admin review."
    )
    return redirect("company_pending")


# def company_resubmit(request):
#     user_id = request.session.get("pending_user_id")
#     if not user_id:
#         return redirect("login")

#     try:
#         user = CustomUser.objects.get(pk=user_id, role="COMPANY")
#     except CustomUser.DoesNotExist:
#         return redirect("login")
 
#     if request.method == "POST":
#         # Resubmit logic same as registration
#         return company_registration(request)

#     return render(request, "accounts/company_resubmit.html", {"user": user})    

def company_resubmit(request):
    # ── User dhundo — 2 tarike ──
    # 1. Already logged in hai (approved company ne rollback li)
    # 2. Session mein pending_user_id hai (login ke baad redirect)
    user = None

    if request.user.is_authenticated and request.user.role == "COMPANY":
        user = request.user
    else:
        user_id = request.session.get("pending_user_id")
        if user_id:
            try:
                user = CustomUser.objects.get(pk=user_id, role="COMPANY")
            except CustomUser.DoesNotExist:
                pass

    if user is None:
        return redirect("login")

    # ── Profile dhundo ──
    try:
        profile = CompanyProfile.objects.get(user=user)
    except CompanyProfile.DoesNotExist:
        request.session["pending_user_id"] = user.pk
        return redirect("company_registration")

    # ── Status check — sirf REJECTED ya ROLLBACK allow karo ──
    status = profile.company_status or "PENDING"
    if status not in ("REJECTED", "ROLLBACK"):
        if user.is_approved:
            return redirect("company:company_dashboard")
        return redirect("company_pending")

    # ── Latest rejection fetch karo ──
    latest_rejection = CompanyRejection.objects.filter(
        company=profile
    ).order_by('-id').first()

    # ── POST — save karo ──
    if request.method == "POST":
        if latest_rejection:
            if latest_rejection.trade_name:
                profile.trade_name = request.POST.get("trade_name", profile.trade_name)
            if latest_rejection.legal_name:
                profile.legal_name = request.POST.get("legal_name", profile.legal_name)
            if latest_rejection.ntn_number:
                profile.ntn_number = request.POST.get("ntn_number", profile.ntn_number)
            if latest_rejection.company_email:
                profile.company_email = request.POST.get("company_email", profile.company_email)
            if latest_rejection.company_type:
                profile.company_type = request.POST.get("company_type", profile.company_type)
            if latest_rejection.industry:
                profile.industry = request.POST.get("industry", profile.industry)
            if latest_rejection.website:
                profile.website = request.POST.get("website", profile.website)
            if latest_rejection.country:
                profile.country = request.POST.get("country", profile.country)
            if latest_rejection.province:
                profile.province = request.POST.get("province", profile.province)
            if latest_rejection.city:
                profile.city = request.POST.get("city", profile.city)
            if latest_rejection.legal_address:
                profile.legal_address = request.POST.get("legal_address", profile.legal_address)
            if latest_rejection.overview:
                profile.overview = request.POST.get("overview", profile.overview)
            if latest_rejection.logo and request.FILES.get("logo"):
                profile.logo = request.FILES["logo"]

        # Status wapas PENDING karo
        profile.company_status = "PENDING"
        profile.save()

        # Session set karo taake pending page user dhund sake
        request.session["pending_user_id"] = user.pk

        messages.success(request, "Your updates have been resubmitted successfully!")
        return redirect("company_pending")

    context = {
        "user":             user,
        "profile":          profile,
        "latest_rejection": latest_rejection,
        "status":           status,
    }
    return render(request, "accounts/company_resubmit.html", context)




# def company_resubmit(request):
#     """
#     Company ko resubmit page dikhao jab:
#     1. Admin ne reject/rollback kiya ho.
#     """
#     # ── Step 1: User dhundo ──
#     user = None
#     if request.user.is_authenticated and request.user.role == 'COMPANY':
#         user = request.user

#     if user is None:
#         user_id = request.session.get('pending_user_id')
#         if user_id:
#             try:
#                 user = CustomUser.objects.get(pk=user_id, role='COMPANY')
#             except CustomUser.DoesNotExist:
#                 pass

#     if user is None:
#         return redirect('accounts:login')

#     # ── Step 2: Profile dhundo ──
#     try:
#         profile = CompanyProfile.objects.get(user=user)
#     except CompanyProfile.DoesNotExist:
#         request.session['pending_user_id'] = user.pk
#         return redirect('accounts:company_registration') # Aapke form ka name

#     # ── Step 3: Latest rejection dhundo ──
#     latest_rejection = CompanyRejection.objects.filter(
#         company=profile
#     ).order_by('-created_at').first()

#     # ── Step 4: POST — Save Karo ──
#     if request.method == 'POST':
#         field_map = {
#             'trade_name':    'trade_name',
#             'legal_name':    'legal_name',
#             'ntn_number':    'ntn_number',
#             'company_email': 'company_email',
#             'company_type':  'company_type',
#             'industry':      'industry',
#             'website':       'website',
#             'country':       'country',
#             'province':      'province',
#             'city':          'city',
#             'legal_address': 'legal_address',
#             'overview':      'overview',
#         }

#         # Agar admin ne field ko true marked (reject) kiya hai toh hi update allow karo
#         if latest_rejection:
#             for field_name, model_attr in field_map.items():
#                 is_rejected = getattr(latest_rejection, field_name, False)
#                 if is_rejected:
#                     val = request.POST.get(field_name, '').strip()
#                     if val:
#                         setattr(profile, model_attr, val)

#             # Logo upload field handle karein
#             if latest_rejection.logo and 'logo' in request.FILES:
#                 profile.logo = request.FILES['logo']

#         # AttributeError FIX: status ki jagah company_status use karein
#         profile.company_status = 'PENDING'
#         profile.save()

#         user.is_approved = False
#         user.save()

#         request.session['pending_user_id'] = user.pk
#         messages.success(request, "Your profile has been resubmitted for review!")
#         return redirect('accounts:company_pending')

#     # ── Step 5: Context ──
#     context = {
#         'user':             user,
#         'profile':          profile,
#         'latest_rejection': latest_rejection,
#         'admin_message':    latest_rejection.message if latest_rejection else '',
#         'company_name':     profile.trade_name or user.username,
#         'profile_status':   profile.company_status, # company_status use kiya
#     }
#     return render(request, 'accounts/company_resubmit.html', context)

def logout_view(request):
    logout(request) 
    return redirect('accounts:login')