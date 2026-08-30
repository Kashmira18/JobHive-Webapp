import json

from django.test import TestCase, RequestFactory, override_settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from accounts.models import CompanyProfile
from billing.models import CompanyCredit, PaymentLog, SubscriptionPlan, CompanySubscription
from billing.middleware import CreditResetMiddleware
from billing.services import is_mock_payment, sign_payload
from job.models import JobPost

User = get_user_model()

class CreditSystemTests(TestCase):
    def setUp(self):
        # 1. Create a user and company
        self.user = User.objects.create_user(username="testcompany", email="test@company.com", password="password123", role="COMPANY")
        self.company = CompanyProfile.objects.create(user=self.user, trade_name="Test Company", company_status="APPROVED")
        
        # 2. Create custom subscription plans
        self.free_plan = SubscriptionPlan.objects.create(
            name="Free Plan",
            price=0,
            job_post_limit=3,
            monthly_credits=5
        )
        self.pro_plan = SubscriptionPlan.objects.create(
            name="Pro Plan",
            price=2999,
            job_post_limit=10,
            monthly_credits=20
        )
        
        # Setup subscription
        self.sub, _ = CompanySubscription.objects.get_or_create(company=self.company)
        self.sub.current_plan = self.free_plan
        self.sub.status = 'Active'
        self.sub.save()

        # Setup credits
        self.credits, _ = CompanyCredit.objects.get_or_create(company=self.company)
        self.credits.subscription_credits = 5
        self.credits.addon_credits = 2
        self.credits.reset_date = timezone.now() + timedelta(days=30)
        self.credits.save()

    def test_split_credits_and_available_credits_property(self):
        """Test that subscription_credits and addon_credits are split and available_credits is their sum."""
        self.assertEqual(self.credits.subscription_credits, 5)
        self.assertEqual(self.credits.addon_credits, 2)
        self.assertEqual(self.credits.available_credits, 7)

    def test_deduction_priority(self):
        """Test that subscription credits are deducted first, then addon credits."""
        # First deduction: subscription_credits decreases by 1
        success = self.credits.deduct_credit()
        self.assertTrue(success)
        self.assertEqual(self.credits.subscription_credits, 4)
        self.assertEqual(self.credits.addon_credits, 2)
        
        # Deduct remaining subscription credits
        for _ in range(4):
            self.credits.deduct_credit()
        self.assertEqual(self.credits.subscription_credits, 0)
        self.assertEqual(self.credits.addon_credits, 2)
        
        # Next deduction: addon_credits decreases by 1
        success = self.credits.deduct_credit()
        self.assertTrue(success)
        self.assertEqual(self.credits.subscription_credits, 0)
        self.assertEqual(self.credits.addon_credits, 1)

        # Deduct last addon credit
        success = self.credits.deduct_credit()
        self.assertTrue(success)
        self.assertEqual(self.credits.available_credits, 0)

        # Further deduction should fail
        success = self.credits.deduct_credit()
        self.assertFalse(success)

    def test_reset_logic_expires_subscription_credits_only(self):
        """Test check_and_reset_credits resets subscription_credits back to default plan amount and keeps addon_credits."""
        # Modify credits
        self.credits.subscription_credits = 1
        self.credits.addon_credits = 10
        self.credits.reset_date = timezone.now() - timedelta(minutes=5) # Past date
        self.credits.save()

        # Run reset check
        reset_happened = self.credits.check_and_reset_credits()
        self.assertTrue(reset_happened)
        
        # Reload from DB
        self.credits.refresh_from_db()
        
        # subscription_credits should be reset to free_plan's default (5)
        self.assertEqual(self.credits.subscription_credits, 5)
        # addon_credits remains untouched
        self.assertEqual(self.credits.addon_credits, 10)
        # reset_date should be in the future now
        self.assertTrue(self.credits.reset_date > timezone.now())

    def test_reset_date_not_passed(self):
        """Test check_and_reset_credits does not reset if reset_date has not passed."""
        self.credits.subscription_credits = 1
        self.credits.addon_credits = 10
        future_date = timezone.now() + timedelta(days=5)
        self.credits.reset_date = future_date
        self.credits.save()

        reset_happened = self.credits.check_and_reset_credits()
        self.assertFalse(reset_happened)

        self.credits.refresh_from_db()
        self.assertEqual(self.credits.subscription_credits, 1)
        self.assertEqual(self.credits.addon_credits, 10)
        self.assertEqual(self.credits.reset_date, future_date)

    def test_middleware_invokes_reset(self):
        """Test that the middleware performs the reset check for logged-in company users."""
        self.credits.subscription_credits = 0
        self.credits.addon_credits = 5
        self.credits.reset_date = timezone.now() - timedelta(hours=1)
        self.credits.save()

        factory = RequestFactory()
        request = factory.get('/company/dashboard/')
        request.user = User.objects.get(pk=self.user.pk)

        middleware = CreditResetMiddleware(lambda req: None)
        middleware.process_request(request)

        self.credits.refresh_from_db()
        self.assertEqual(self.credits.subscription_credits, 5)
        self.assertEqual(self.credits.addon_credits, 5)
        self.assertTrue(self.credits.reset_date > timezone.now())


@override_settings(
    PAYMENT_GATEWAYS={
        "JazzCash": {
            "merchant_id": "merchant",
            "password": "password",
            "integrity_salt": "test-secret",
            "store_id": "store",
            "sandbox_url": "",
            "production_url": "",
        },
        "EasyPaisa": {
            "merchant_id": "merchant",
            "password": "password",
            "integrity_salt": "test-secret",
            "store_id": "store",
            "sandbox_url": "",
            "production_url": "",
        },
    }
)
class PaymentCallbackTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="paymentcompany",
            email="payment@example.com",
            password="password123",
            role="COMPANY",
        )
        self.company = CompanyProfile.objects.create(
            user=self.user,
            trade_name="Payment Company",
            company_status="APPROVED",
        )
        self.payment = PaymentLog.objects.create(
            company=self.company,
            transaction_id="TXN-CALLBACK-1",
            account_number="03001234567",
            amount=500,
            gateway="JazzCash",
        )

    def callback_payload(self, status="SUCCESS"):
        payload = {
            "transaction_id": self.payment.transaction_id,
            "status": status,
        }
        payload["signature"] = sign_payload(payload, "test-secret")
        return payload

    def test_valid_callback_confirms_payment_without_allocating_benefits(self):
        response = self.client.post(
            reverse("billing:payment_callback"),
            data=json.dumps(self.callback_payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.company.credits.refresh_from_db()
        self.assertEqual(self.payment.status, "Pending")
        self.assertEqual(self.company.credits.addon_credits, 0)

    def test_duplicate_callback_does_not_add_credits_twice(self):
        payload = self.callback_payload()
        url = reverse("billing:payment_callback")

        self.client.post(url, data=json.dumps(payload), content_type="application/json")
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.company.credits.refresh_from_db()
        self.assertEqual(self.company.credits.addon_credits, 0)

    def test_invalid_callback_signature_is_rejected(self):
        payload = self.callback_payload()
        payload["signature"] = "invalid"

        response = self.client.post(
            reverse("billing:payment_callback"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "Pending")

    def test_sandbox_mode_uses_mock_payment_without_gateway_credentials(self):
        with self.settings(
            PAYMENT_MODE="sandbox",
            PAYMENT_GATEWAYS={"JazzCash": {"merchant_id": "", "password": "", "integrity_salt": "", "store_id": ""}},
        ):
            self.assertTrue(is_mock_payment("JazzCash"))

    def test_placeholder_credentials_use_mock_payment_in_production_mode(self):
        with self.settings(
            PAYMENT_MODE="production",
            PAYMENT_GATEWAYS={
                "EasyPaisa": {
                    "merchant_id": "EP123456",
                    "password": "test_ep_password",
                    "integrity_salt": "test_ep_salt",
                    "store_id": "test_ep_store",
                }
            },
        ):
            self.assertTrue(is_mock_payment("EasyPaisa"))

    def test_pay_now_creates_pending_payment_without_credits(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("billing:initiate_payment"),
            {
                "gateway": "JazzCash",
                "mobile_number": "03001234567",
                "package_type": "Credit_Bundle",
            },
        )

        self.assertEqual(response.status_code, 302)
        payment = PaymentLog.objects.latest("id")
        self.company.credits.refresh_from_db()
        self.assertEqual(payment.status, "Pending")
        self.assertEqual(self.company.credits.addon_credits, 0)
        self.assertIn(
            "Payment submitted successfully! It is currently under review by Admin.",
            [str(message) for message in get_messages(response.wsgi_request)],
        )

    def test_admin_approval_allocates_credits(self):
        admin = User.objects.create_superuser(
            username="paymentadmin",
            email="paymentadmin@example.com",
            password="password123",
        )
        self.client.force_login(admin)

        response = self.client.get(
            reverse("custom_admin:approve_payment", args=[self.payment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.company.credits.refresh_from_db()
        self.assertEqual(self.payment.status, "Approved")
        self.assertEqual(self.company.credits.addon_credits, 10)

