import uuid
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentLog, SubscriptionPlan
from .services import (
    PaymentGatewayError,
    gateway_config,
    send_payment_request,
    settle_payment,
    is_mock_payment,
    verify_signature,
)

logger = logging.getLogger(__name__)

@login_required(login_url='accounts:login')
def initiate_payment(request):
    if request.method == 'POST':
        company = getattr(request.user, 'company_profile', None)
        if not company:
            return redirect('home')

        gateway = request.POST.get('gateway')
        mobile_number = request.POST.get('mobile_number')
        package_type = request.POST.get('package_type') # 'Pro_Plan' or 'Credit_Bundle'

        if gateway not in settings.PAYMENT_GATEWAYS:
            messages.error(request, "Please select a supported payment gateway.")
            return redirect(reverse('company:company_account_settings') + '?tab=billing')
        
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
        payment_log = PaymentLog.objects.create(
            company=company,
            plan=plan,
            transaction_id=txn_id,
            account_number=mobile_number,
            amount=amount,
            gateway=gateway,
            status='Pending'
        )

        try:
            gateway_config(gateway)
            if not is_mock_payment(gateway):
                send_payment_request(
                    payment_log,
                    request.build_absolute_uri(reverse("billing:payment_callback")),
                )
        except PaymentGatewayError as exc:
            payment_log.delete()
            messages.error(request, str(exc))
            return redirect(reverse('company:company_account_settings') + '?tab=billing')

        messages.info(request, "Payment submitted successfully! It is currently under review by Admin.")
        
        return redirect(reverse('company:company_account_settings') + '?tab=billing')

    return redirect('home')
def simulate_webhook_success(txn_id, gateway, package_type):
    """Backward-compatible helper for existing development callers."""
    log = PaymentLog.objects.get(transaction_id=txn_id)
    return settle_payment(log, "SUCCESS")


@csrf_exempt
def payment_callback(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else request.POST.dict()
        transaction_id = payload.get("transaction_id") or payload.get("pp_TxnRefNo")
        signature = request.headers.get("X-Signature") or payload.pop("signature", None)
        payment_log = PaymentLog.objects.select_related("company").get(
            transaction_id=transaction_id
        )
        config = gateway_config(payment_log.gateway)
        if not verify_signature(payload, signature, config["integrity_salt"]):
            return JsonResponse({"success": False, "error": "Invalid signature."}, status=400)
        # Gateway confirmation does not grant benefits; an admin must approve it.
        return JsonResponse({"success": True}, status=200)
    except (PaymentLog.DoesNotExist, PaymentGatewayError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Invalid payment callback."}, status=400)
    except Exception:
        logger.exception("Unexpected payment callback failure")
        return JsonResponse({"success": False, "error": "Payment processing is temporarily unavailable."}, status=503)


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
        payment_log = PaymentLog.objects.create(
            company=company_profile,
            plan=plan,
            transaction_id=txn_id,
            account_number=account_number,
            amount=plan.price,
            gateway=gateway,
            status='Pending'
        )
        
        try:
            gateway_config(gateway)
            if not is_mock_payment(gateway):
                send_payment_request(
                    payment_log,
                    request.build_absolute_uri(reverse("billing:payment_callback")),
                )
        except PaymentGatewayError as exc:
            payment_log.delete()
            messages.error(request, str(exc))
            return redirect(reverse('company:company_account_settings') + '?tab=billing')

        messages.info(request, "Payment submitted successfully! It is currently under review by Admin.")
        return redirect(reverse('company:company_account_settings') + '?tab=billing')

    return render(request, 'billing/checkout.html', {'plan': plan})