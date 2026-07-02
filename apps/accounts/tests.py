from django.test import TestCase
from django.urls import reverse

from .models import CompanyProfile, CustomUser


class CompanyRegistrationRedirectTests(TestCase):
    def test_company_registration_post_redirects_to_pending_page(self):
        user = CustomUser.objects.create_user(
            username="companyuser",
            email="company@example.com",
            password="StrongPass123!",
            role="COMPANY",
        )
        session = self.client.session
        session["pending_user_id"] = user.pk
        session.save()

        response = self.client.post(
            reverse("accounts:company_registration"),
            {
                "first_name": "Test",
                "last_name": "Company",
                "owner_phone": "1234567890",
                "designation": "Manager",
                "trade_name": "Test Trade",
                "legal_name": "Test Legal",
                "company_type": "LLC",
                "industry": "IT",
                "country": "PK",
                "city": "Karachi",
                "legal_address": "123 Main Street",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:company_pending"))
        self.assertTrue(CompanyProfile.objects.filter(user=user).exists())
