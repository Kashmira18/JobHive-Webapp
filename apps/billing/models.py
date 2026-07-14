from django.db import models
from django.utils import timezone
from accounts.models import CompanyProfile # Adjust import path
from candidate.models import CandidateProfile # Adjust import path


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    job_post_limit = models.IntegerField(help_text="Max active jobs allowed")
    monthly_credits = models.IntegerField(help_text="Credits added per month for profile unlocks")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - PKR {self.price}"

class CompanySubscription(models.Model):
    company = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, related_name='subscription')
    current_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Expired', 'Expired')], default='Expired')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.trade_name} - {self.status}"

class CompanyCredit(models.Model):
    company = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, related_name='credits')
    subscription_credits = models.IntegerField(default=0)
    addon_credits = models.IntegerField(default=0)
    reset_date = models.DateTimeField(null=True, blank=True)

    @property
    def available_credits(self):
        return self.subscription_credits + self.addon_credits

    def deduct_credit(self):
        if self.subscription_credits > 0:
            self.subscription_credits -= 1
            self.save()
            return True
        elif self.addon_credits > 0:
            self.addon_credits -= 1
            self.save()
            return True
        return False

    def check_and_reset_credits(self):
        if self.reset_date and self.reset_date <= timezone.now():
            from datetime import timedelta
            try:
                sub = self.company.subscription
                default_credits = sub.current_plan.monthly_credits if sub.current_plan else 0
            except Exception:
                default_credits = 0

            self.subscription_credits = default_credits
            while self.reset_date <= timezone.now():
                self.reset_date += timedelta(days=30)
            self.save()
            return True
        return False

class ProfileUnlock(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'candidate')

class PaymentLog(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    account_number = models.CharField(max_length=20, null=True, blank=True) # Added to store sender's wallet number
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gateway = models.CharField(max_length=20, choices=[('EasyPaisa', 'EasyPaisa'), ('JazzCash', 'JazzCash')])
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} - {self.transaction_id} - {self.status}"