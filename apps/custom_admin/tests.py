from django.test import TestCase
from django.urls import reverse

from accounts.models import CompanyProfile, CustomUser


class CustomAdminCompanyListTests(TestCase):
    def test_admin_company_page_shows_companies_by_status(self):
        pending_company = CustomUser.objects.create_user(
            username="acme",
            email="acme@example.com",
            password="secret123",
            role="COMPANY",
        )
        CompanyProfile.objects.create(
            user=pending_company,
            trade_name="Acme Corp",
            company_status="PENDING",
        )

        rollback_company = CustomUser.objects.create_user(
            username="globex",
            email="globex@example.com",
            password="secret123",
            role="COMPANY",
        )
        CompanyProfile.objects.create(
            user=rollback_company,
            trade_name="Globex Ltd",
            company_status="ROLLBACK",
        )

        response = self.client.get(reverse("custom_admin:admin_company"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "acme@example.com")
        self.assertContains(response, "Acme Corp")
        self.assertContains(response, "globex@example.com")
        self.assertContains(response, "Globex Ltd")
