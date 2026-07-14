from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from accounts.models import CompanyProfile
from billing.models import CompanyCredit, SubscriptionPlan, CompanySubscription
from billing.middleware import CreditResetMiddleware
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

        # Mock request
        factory = RequestFactory()
        request = factory.get('/company/dashboard/')
        request.user = User.objects.get(pk=self.user.pk)
        
        middleware = CreditResetMiddleware(lambda req: None)
        middleware.process_request(request)

        # Verify credits were reset
        self.credits.refresh_from_db()
        self.assertEqual(self.credits.subscription_credits, 5)
        self.assertEqual(self.credits.addon_credits, 5)
        self.assertTrue(self.credits.reset_date > timezone.now())
