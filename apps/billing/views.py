import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import PaymentLog, SubscriptionPlan

@login_required(login_url='accounts:login')
def initiate_payment(request):
    if request.method == 'POST':
        company = getattr(request.user, 'company_profile', None)
        if not company:
            return redirect('home')

        gateway = request.POST.get('gateway')
        mobile_number = request.POST.get('mobile_number')
        package_type = request.POST.get('package_type') # 'Pro_Plan' or 'Credit_Bundle'
        
        # 1. Safely fetch the plan from the database
        if package_type == 'Pro_Plan':
            # Use filter().first() so it doesn't crash if the plan is missing
            plan = SubscriptionPlan.objects.filter(name='Professional').first()
            amount = plan.price if plan else 2999
        else:
            plan = None
            amount = 500 # Default price for credit bundle
            
        # 2. Generate unique transaction ID
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # 3. Create a PENDING log for the Admin to verify
        PaymentLog.objects.create(
            company=company,
            plan=plan,
            transaction_id=txn_id,
            account_number=mobile_number,
            amount=amount,
            gateway=gateway,
            status='Pending'
        )

        messages.success(request, f"Your payment request via {gateway} has been submitted! It is now pending Admin verification.")
        
        return redirect(reverse('company:company_account_settings') + '?tab=billing')

    return redirect('home')
def simulate_webhook_success(txn_id, gateway, package_type):
    """Mock webhook processor to update DB instantly for development"""
    log = PaymentLog.objects.get(transaction_id=txn_id)
    log.status = 'Approved'
    log.save()
    
    if package_type == 'Pro_Plan':
        pro_plan = SubscriptionPlan.objects.filter(name__icontains='Professional').first()
        sub = log.company.subscription
        sub.current_plan = pro_plan
        sub.status = 'Active'
        sub.save()
    else:
        # Credit bundle top-up
        credits = log.company.credits
        credits.available_credits += 10
        credits.save()


@login_required(login_url='accounts:login')
def checkout_view(request, plan_id):
    if request.user.role != 'COMPANY':
        return redirect('home')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    company_profile = request.user.company_profile

    if request.method == 'POST':
        gateway = request.POST.get('gateway')
        account_number = request.POST.get('account_number')
        
        # Generate a unique Txn ID
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # Create Pending Payment Log
        PaymentLog.objects.create(
            company=company_profile,
            plan=plan,
            transaction_id=txn_id,
            account_number=account_number,
            amount=plan.price,
            gateway=gateway,
            status='Pending'
        )
        
        messages.success(request, f"Your payment request for {plan.name} has been submitted. It is pending admin verification.")
        return redirect(reverse('company:company_account_settings') + '?tab=billing')

    return render(request, 'billing/checkout.html', {'plan': plan})