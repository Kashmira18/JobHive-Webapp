import hashlib
import hmac
import json
import urllib.error
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import CompanyCredit, CompanySubscription, PaymentLog


SUCCESS_STATUSES = {"1", "SUCCESS", "PAID", "COMPLETED", "APPROVED"}
DUMMY_CREDENTIAL_VALUES = {"", "dummy", "test", "changeme", "your_merchant_id"}


class PaymentGatewayError(Exception):
    pass


def is_mock_payment(gateway):
    if settings.PAYMENT_MODE == "sandbox":
        return True
    config = settings.PAYMENT_GATEWAYS.get(gateway, {})
    for key in ("merchant_id", "password", "integrity_salt", "store_id"):
        value = str(config.get(key, "")).strip().lower()
        if value in DUMMY_CREDENTIAL_VALUES or value.startswith("test_"):
            return True
        if value.startswith(("mc123", "ep123", "your_")) or "dummy" in value:
            return True
    return False


def gateway_config(gateway):
    try:
        config = settings.PAYMENT_GATEWAYS[gateway]
    except KeyError as exc:
        raise PaymentGatewayError("The selected payment gateway is not supported.") from exc

    required = ("merchant_id", "password", "integrity_salt", "store_id")
    if not is_mock_payment(gateway) and any(not config.get(key) for key in required):
        raise PaymentGatewayError(
            f"{gateway} payments are not configured yet. Please contact support."
        )
    return config


def signing_text(payload):
    return "&".join(
        f"{key}={payload[key]}"
        for key in sorted(payload)
        if payload[key] not in (None, "")
    )


def sign_payload(payload, secret):
    return hmac.new(
        secret.encode("utf-8"),
        signing_text(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(payload, signature, secret):
    return bool(signature) and hmac.compare_digest(
        sign_payload(payload, secret), signature
    )


def build_payment_payload(payment_log, callback_url):
    config = gateway_config(payment_log.gateway)
    payload = {
        "merchant_id": config["merchant_id"],
        "password": config["password"],
        "store_id": config["store_id"],
        "transaction_id": payment_log.transaction_id,
        "amount": str(payment_log.amount),
        "account_number": payment_log.account_number or "",
        "callback_url": callback_url,
    }
    return payload, sign_payload(payload, config["integrity_salt"])


def send_payment_request(payment_log, callback_url):
    if is_mock_payment(payment_log.gateway):
        payload, signature = build_payment_payload(payment_log, callback_url)
        return {"status": "SUCCESS", "transaction_id": payment_log.transaction_id, "signature": signature}

    payload, signature = build_payment_payload(payment_log, callback_url)
    config = settings.PAYMENT_GATEWAYS[payment_log.gateway]
    endpoint = config[f"{settings.PAYMENT_MODE}_url"]
    if not endpoint:
        raise PaymentGatewayError(
            f"{payment_log.gateway} {settings.PAYMENT_MODE} endpoint is not configured."
        )

    request_body = json.dumps({**payload, "signature": signature}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=request_body,
        headers={"Content-Type": "application/json", "X-Signature": signature},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.PAYMENT_GATEWAY_TIMEOUT) as response:
            body = response.read().decode("utf-8")
            if response.status < 200 or response.status >= 300:
                raise PaymentGatewayError("The payment gateway rejected the request.")
            return json.loads(body) if body else {}
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise PaymentGatewayError(
            "The payment service is temporarily unavailable. Please try again."
        ) from exc


@transaction.atomic
def settle_payment(payment_log, status):
    payment_log = PaymentLog.objects.select_related("plan").select_for_update(
        of=("self",)
    ).get(pk=payment_log.pk)
    if payment_log.status == "Approved":
        return payment_log
    if status not in SUCCESS_STATUSES:
        payment_log.status = "Rejected"
        payment_log.save(update_fields=["status"])
        return payment_log

    payment_log.status = "Approved"
    payment_log.save(update_fields=["status"])
    credits, _ = CompanyCredit.objects.get_or_create(company=payment_log.company)
    if payment_log.plan:
        subscription, _ = CompanySubscription.objects.get_or_create(company=payment_log.company)
        subscription.current_plan = payment_log.plan
        subscription.status = "Active"
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timedelta(days=30)
        subscription.save()
        credits.subscription_credits = payment_log.plan.monthly_credits
        credits.reset_date = timezone.now() + timedelta(days=30)
    else:
        credits.addon_credits += 10
    credits.save()
    return payment_log
