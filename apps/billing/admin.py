from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import (
    SubscriptionPlan,
    CompanySubscription,
    CompanyCredit,
    PaymentLog,
    ProfileUnlock,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'job_post_limit', 'monthly_credits', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'current_plan', 'status', 'start_date', 'end_date')
    list_filter = ('status',)
    search_fields = ('company__trade_name',)


@admin.register(CompanyCredit)
class CompanyCreditAdmin(admin.ModelAdmin):
    list_display = ('company', 'subscription_credits', 'addon_credits', 'available_credits', 'reset_date')
    search_fields = ('company__trade_name',)


@admin.register(ProfileUnlock)
class ProfileUnlockAdmin(admin.ModelAdmin):
    list_display = ('company', 'candidate', 'unlocked_at')
    list_filter = ('unlocked_at',)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'company', 'plan', 'amount', 'gateway', 'status', 'timestamp')
    list_filter = ('status', 'gateway', 'timestamp')
    search_fields = ('transaction_id', 'company__trade_name', 'account_number')
    readonly_fields = ('transaction_id', 'company', 'plan', 'amount', 'gateway', 'account_number', 'timestamp')
    actions = ['approve_payments', 'reject_payments']

    @admin.action(description="✅ Approve selected payments")
    def approve_payments(self, request, queryset):
        pending = queryset.filter(status='Pending')
        approved_count = 0

        for log in pending:
            log.status = 'Approved'
            log.save()

            if log.plan:
                # Subscription upgrade — activate plan
                try:
                    sub = log.company.subscription
                except CompanySubscription.DoesNotExist:
                    sub = CompanySubscription.objects.create(
                        company=log.company,
                        current_plan=log.plan,
                        status='Active',
                    )
                else:
                    sub.current_plan = log.plan
                    sub.status = 'Active'
                    sub.end_date = timezone.now() + timedelta(days=30)
                    sub.save()

                # Also grant the plan's monthly credits
                try:
                    credits = log.company.credits
                except CompanyCredit.DoesNotExist:
                    credits = CompanyCredit.objects.create(
                        company=log.company,
                        subscription_credits=log.plan.monthly_credits,
                        addon_credits=0,
                        reset_date=timezone.now() + timedelta(days=30),
                    )
                else:
                    credits.subscription_credits = log.plan.monthly_credits
                    credits.reset_date = timezone.now() + timedelta(days=30)
                    credits.save()
            else:
                # Credit bundle purchase — add 10 credits
                try:
                    credits = log.company.credits
                except CompanyCredit.DoesNotExist:
                    credits = CompanyCredit.objects.create(
                        company=log.company,
                        subscription_credits=0,
                        addon_credits=10,
                    )
                else:
                    credits.addon_credits += 10
                    credits.save()

            approved_count += 1

        self.message_user(
            request,
            f"✅ {approved_count} payment(s) approved and activated successfully.",
            messages.SUCCESS,
        )

    @admin.action(description="❌ Reject selected payments")
    def reject_payments(self, request, queryset):
        updated = queryset.filter(status='Pending').update(status='Rejected')
        self.message_user(
            request,
            f"❌ {updated} payment(s) have been rejected.",
            messages.WARNING,
        )
