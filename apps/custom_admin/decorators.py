from functools import wraps
from django.shortcuts import redirect


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