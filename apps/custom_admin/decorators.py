from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_login_required(view_func):
    """
    Custom decorator — sirf logged-in admin users access kar saktay hain.
    Agar user logged in nahi ya staff nahi to admin login par redirect karta hai.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("custom_admin:login")
        return view_func(request, *args, **kwargs)
    return wrapper

# def candidate_login_required(view_func):
#     """
#     Custom decorator — sirf logged-in candidate users access kar saktay hain.
#     Agar user logged in nahi to login page par redirect karta hai.
#     Agar user candidate nahi (e.g. company/admin) to unauthorized message dikhata hai.
#     """
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         # Check 1: User logged in hai ya nahi
#         if not request.user.is_authenticated:
#             messages.error(request, "Pehle login karein.")
#             return redirect("accounts:login")
        
#         # Check 2: User candidate role ka hai ya nahi
#         if not hasattr(request.user, 'role') or request.user.role != 'candidate':
#             messages.error(request, "Aap candidate nahi hain.")
#             return redirect("accounts:login")
        
#         return view_func(request, *args, **kwargs)
#     return wrapper