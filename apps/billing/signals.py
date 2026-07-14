from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from accounts.models import CompanyProfile
from .models import CompanySubscription, CompanyCredit, SubscriptionPlan

@receiver(post_save, sender=CompanyProfile)
def create_billing_profiles(sender, instance, created, **kwargs):
    if created:
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free",
            defaults={'price': 0, 'job_post_limit': 3, 'monthly_credits': 0}
        )
        CompanySubscription.objects.create(
            company=instance, 
            current_plan=free_plan, 
            status='Active'
        )
        CompanyCredit.objects.create(
            company=instance,
            subscription_credits=free_plan.monthly_credits,
            addon_credits=0,
            reset_date=timezone.now() + timedelta(days=30)
        )