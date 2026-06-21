# # apps/company/decorators.py
# from django.shortcuts import redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required

# def approved_company_required(view_func):
#     """
#     Custom decorator — ensures:
#     1. User is authenticated
#     2. User role is COMPANY
#     3. Company profile exists and is APPROVED
#     """
#     @login_required
#     def wrapper(request, *args, **kwargs):
#         if request.user.role != "COMPANY":
#             messages.error(request, "Access denied. Company accounts only.")
#             return redirect("login")
 
#         # Safe check bina try-except crash ke:
#         profile = None
#         if hasattr(request.user, 'company_profile') and request.user.company_profile:
#             profile = request.user.company_profile
#         elif hasattr(request.user, 'companyprofile') and request.user.companyprofile:
#             profile = request.user.companyprofile

#         # Agar dono surton mein profile na mile:
#         if not profile:
#             messages.warning(request, "Please complete your company registration first.")
#             return redirect("company_registration")
 
#         # Status check
#         if profile.company_status != "APPROVED":
#             messages.warning(request, "Your company account must be approved before posting jobs.")
#             return redirect("company_pending")
 
#         return view_func(request, *args, **kwargs)
#     return wrapper














# apps/company/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def approved_company_required(view_func):
    """
    Custom decorator — ensures:
    1. User is authenticated
    2. User role is COMPANY
    3. Company profile exists and is APPROVED
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != "COMPANY":
            messages.error(request, "Access denied. Company accounts only.")
            return redirect("login")
 
        # Safe check bina try-except crash ke:
        profile = None
        if hasattr(request.user, 'company_profile') and request.user.company_profile:
            profile = request.user.company_profile
        elif hasattr(request.user, 'companyprofile') and request.user.companyprofile:
            profile = request.user.companyprofile

        # Agar dono surton mein profile na mile:
        if not profile:
            messages.warning(request, "Please complete your company registration first.")
            return redirect("company_registration")
 
        # ✨ CHNAGE HERE: Status check ko case-insensitive aur user check ke sath flexible banaya
        status = profile.company_status or "PENDING"
        
        # Agar direct user model par b APPROVED ho ya status text match kare
        is_profile_approved = status in ["APPROVED", "Approved", "approved"]
        is_user_approved = hasattr(request.user, 'is_approved') and request.user.is_approved

        if not (is_profile_approved or is_user_approved):
            messages.warning(request, "Your company account must be approved before posting jobs.")
            return redirect("company_pending")
 
        return view_func(request, *args, **kwargs)
    return wrapper