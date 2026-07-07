from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import ProfileUnlock

def require_credit_to_view(view_func):
    @wraps(view_func)
    def _wrapped_view(request, candidate_id, *args, **kwargs):
        company = getattr(request.user, 'company_profile', None)
        if not company:
            return redirect('home')

        # Check if already unlocked
        has_unlocked = ProfileUnlock.objects.filter(company=company, candidate_id=candidate_id).exists()
        
        if not has_unlocked:
            company_credits = company.credits
            if company_credits.available_credits > 0:
                # Deduct and unlock
                company_credits.deduct_credit()
                ProfileUnlock.objects.create(company=company, candidate_id=candidate_id)
                messages.success(request, "1 credit deducted to unlock this profile.")
            else:
                messages.error(request, "Insufficient credits to view this profile. Please top up.")
                return redirect('/company/dashboard/?tab=billing')
                
        return view_func(request, candidate_id, *args, **kwargs)
    return _wrapped_view