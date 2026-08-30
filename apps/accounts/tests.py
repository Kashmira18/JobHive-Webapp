from unittest.mock import patch
from smtplib import SMTPException

from django.core import mail
from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse
from django.template.loader import render_to_string

from notifications.models import Notification
from .forms import ForgotPasswordForm, LoginForm
from .account_adapter import CustomAccountAdapter
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


class CompanyResubmissionNotificationTests(TestCase):
    def test_company_resubmission_creates_admin_notification(self):
        admin = CustomUser.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="StrongPass123!",
        )
        company = CustomUser.objects.create_user(
            username="companyresubmit",
            email="companyresubmit@example.com",
            password="StrongPass123!",
            role="COMPANY",
        )
        CompanyProfile.objects.create(
            user=company,
            trade_name="Resubmit Co",
            company_status="ROLLBACK",
        )

        self.client.force_login(company)

        response = self.client.post(
            reverse("accounts:company_resubmit"),
            {
                "trade_name": "Resubmit Co Updated",
                "legal_name": "Updated Legal Name",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Notification.objects.filter(
                user=admin,
                notification_type="KYC_RESUBMITTED",
            ).exists()
        )


class GoogleOAuthConfigurationTests(TestCase):
    @override_settings(GOOGLE_CLIENT_ID="", GOOGLE_CLIENT_SECRET="")
    def test_google_login_route_redirects_when_unconfigured(self):
        response = self.client.get("/accounts/google/login/")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

    def test_login_template_uses_allauth_google_provider_url(self):
        html = render_to_string("accounts/login.html", {"form": LoginForm()})

        self.assertIn('href="/accounts/google/login/"', html)

    def test_social_login_redirects_by_user_role(self):
        adapter = CustomAccountAdapter()
        request = self.client.get(reverse("accounts:login"))

        for role, expected_url in (
            ("CANDIDATE", reverse("candidate:candidate_dashboard")),
            ("COMPANY", reverse("company:company_dashboard")),
            ("ADMIN", reverse("custom_admin:admin_dashboard")),
        ):
            user = CustomUser.objects.create_user(
                username=f"oauth_{role.lower()}",
                email=f"{role.lower()}@example.com",
                password="StrongPass123!",
                role=role,
            )
            request.user = user
            self.assertEqual(adapter.get_login_redirect_url(request), expected_url)


class PasswordResetEmailTests(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_forgot_password_sends_link_to_confirm_route(self):
        user = CustomUser.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="StrongPass123!",
            role="CANDIDATE",
        )

        response = self.client.post(
            reverse("accounts:forget_password"), {"email": user.email}
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/auth/reset-password/", mail.outbox[0].alternatives[0][0])

    @patch("accounts.views.send_mail", side_effect=SMTPException("SMTP unavailable"))
    def test_smtp_failure_shows_error_instead_of_crashing(self, send_mail_mock):
        CustomUser.objects.create_user(
            username="smtpuser",
            email="smtp@example.com",
            password="StrongPass123!",
            role="CANDIDATE",
        )

        response = self.client.post(
            reverse("accounts:forget_password"), {"email": "smtp@example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "We couldn't send the reset email right now. Please try again later.",
            [str(message) for message in get_messages(response.wsgi_request)],
        )
        send_mail_mock.assert_called_once()

    def test_forgot_password_form_validates_email(self):
        form = ForgotPasswordForm({"email": "not-an-email"})

        self.assertFalse(form.is_valid())
