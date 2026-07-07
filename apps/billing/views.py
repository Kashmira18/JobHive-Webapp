import uuid
import requests
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PaymentLog, SubscriptionPlan

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        company = request.user.company_profile
        gateway = request.POST.get('gateway')
        mobile_number = request.POST.get('mobile_number')
        package_type = request.POST.get('package_type') # e.g., 'Pro_Plan' or 'Credit_Bundle'
        
        # Determine amount based on package (mock logic)
        amount = 2999 if package_type == 'Pro_Plan' else 500
        
        # Generate unique transaction ID
        txn_id = f"{gateway[:2].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create Pending Log
        PaymentLog.objects.create(
            company=company,
            transaction_id=txn_id,
            amount=amount,
            gateway=gateway
        )

        # Mock API Call to Wallet Provider
        api_url = f"https://api.mock{gateway.lower()}.com/v1/charge"
        payload = {
            "mobile": mobile_number,
            "amount": amount,
            "reference": txn_id,
            "callback_url": f"https://yourdomain.com/billing/webhook/{gateway.lower()}/"
        }
        
        try:
            # Simulate request
            # response = requests.post(api_url, json=payload, timeout=5)
            # In development, we auto-simulate a successful callback
            simulate_webhook_success(txn_id, gateway, package_type)
            messages.success(request, f"Payment request sent to your {gateway} number. Processing...")
        except requests.RequestException:
            messages.error(request, "Gateway timeout. Please try again.")

        return redirect('/company/dashboard/?tab=billing')
    return redirect('home')

def simulate_webhook_success(txn_id, gateway, package_type):
    """Mock webhook processor to update DB instantly for development"""
    log = PaymentLog.objects.get(transaction_id=txn_id)
    log.status = 'Success'
    log.save()
    
    if package_type == 'Pro_Plan':
        pro_plan = SubscriptionPlan.objects.get(name='Professional')
        sub = log.company.subscription
        sub.current_plan = pro_plan
        sub.status = 'Active'
        sub.save()
    else:
        # Credit bundle top-up
        credits = log.company.credits
        credits.available_credits += 10
        credits.save()