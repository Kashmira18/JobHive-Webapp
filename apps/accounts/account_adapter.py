from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.role == "COMPANY":
            return reverse("company:company_dashboard")
        if request.user.role == "ADMIN":
            return reverse("custom_admin:admin_dashboard")
        return reverse("candidate:candidate_dashboard")