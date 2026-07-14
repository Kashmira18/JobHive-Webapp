from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from billing.models import CompanyCredit

class CreditResetMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            company = getattr(request.user, 'company_profile', None)
            if company:
                try:
                    credits = company.credits
                    credits.check_and_reset_credits()
                except CompanyCredit.DoesNotExist:
                    pass
        return None
