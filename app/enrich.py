from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from .models import EnrichRequest


def _h(seed: str) -> int:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _score_0_100(seed: str) -> int:
    return _h(seed) % 101


def _bool(seed: str, threshold_pct: int) -> bool:
    return (_h(seed) % 100) < threshold_pct


def _pick(seed: str, options: List[str]) -> str:
    return options[_h(seed) % len(options)] if options else ""


def _get_seed(req: EnrichRequest) -> str:
    """Generate consistent seed for deterministic mocking"""
    email = str(req.data.email)
    ip = req.data.ip or "0.0.0.0"
    bin_ = ""
    if req.payment and req.payment.card and req.payment.card.bin:
        bin_ = req.payment.card.bin
    bin_ = bin_ or "000000"
    return f"{req.transaction_id}|{email}|{ip}|{bin_}"


def build_mock_emailage(req: EnrichRequest) -> Dict[str, Any]:
    """Build mock Emailage response"""
    seed = _get_seed(req)
    now = datetime.now(timezone.utc).replace(microsecond=0)

    first_seen_days_ago = 30 + (_h(seed + "|first_seen") % 2000)
    last_seen_days_ago = _h(seed + "|last_seen") % 90

    email_first_seen = (now - timedelta(days=first_seen_days_ago)).isoformat()
    email_last_seen = (now - timedelta(days=last_seen_days_ago)).isoformat()

    email_risk = _score_0_100(seed + "|emailage")

    return {
        "score": email_risk,
        "email_first_seen": email_first_seen,
        "email_last_seen": email_last_seen,
        "domain_exists": _bool(seed + "|domain", 92),
        "disposable": _bool(seed + "|disposable", 7),
        "free_provider": _bool(seed + "|free_provider", 55),
    }


def build_mock_threatmetrix(req: EnrichRequest) -> Dict[str, Any]:
    """Build mock ThreatMetrix response"""
    seed = _get_seed(req)
    tm_risk = _score_0_100(seed + "|threatmetrix")

    return {
        "risk_score": tm_risk,
        "policy": _pick(seed + "|policy", ["ALLOW", "REVIEW", "REJECT"]),
        "device_risk": _score_0_100(seed + "|device_risk"),
        "ip_risk": _score_0_100(seed + "|ip_risk"),
        "true_ip": _bool(seed + "|true_ip", 88),
        "bot_detected": _bool(seed + "|bot", 9),
    }


def build_mock_ekata(req: EnrichRequest) -> Dict[str, Any]:
    """Build mock Ekata response"""
    seed = _get_seed(req)
    ekata_conf = _score_0_100(seed + "|ekata")

    return {
        "identity_confidence": ekata_conf,
        "phone_to_name_match": _bool(seed + "|phone_name", 72),
        "address_to_name_match": _bool(seed + "|addr_name", 66),
        "email_to_name_match": _bool(seed + "|email_name", 62),
    }


def build_mock_external_services(req: EnrichRequest) -> Dict[str, Any]:
    """Build all mock external services (backward compatibility)"""
    return {
        "emailage": build_mock_emailage(req),
        "threatmetrix": build_mock_threatmetrix(req),
        "ekata": build_mock_ekata(req),
    }


def build_mock_transaction(req: EnrichRequest) -> Dict[str, Any]:
    seed = f"{req.transaction_id}|{req.data.email}"

    status = _pick(seed + "|status", ["Completed", "Declined", "Review", "Pending"])
    decision = _pick(seed + "|decision", ["APPROVE", "REVIEW", "DECLINE"])

    amount = req.payment.amount if (req.payment and req.payment.amount is not None) else float((_h(seed) % 19999) / 100.0)

    card_payload = {}
    if req.payment and req.payment.card:
        card_payload = {
            "bin": req.payment.card.bin,
            "last4": req.payment.card.last4,
            "network": req.payment.card.network,
        }

    return {
        "transaction_id": req.transaction_id,
        "transaction_time": req.transaction_time.astimezone(timezone.utc).isoformat(),
        "status": status,
        "decision": decision,
        "amounts": {
            "total_amount": round(float(amount), 2),
            "currency": (req.payment.currency if req.payment else "USD") or "USD",
        },
        "channel": req.channel or _pick(seed + "|channel", ["web", "mobile", "ivr"]),
        "merchant": {
            "merchant_id": req.merchant_id or _pick(seed + "|mid", ["M12345", "M67890", "M24680"]),
        },
        "payment": {"card": card_payload},
        "network": {
            "ip": req.data.ip,
            "ip_country": _pick(seed + "|ip_country", ["US", "CA", "MX", "GB", "IN"]),
            "ip_proxy": _bool(seed + "|proxy", 11),
        },
    }


def normalize_response(req: EnrichRequest, dataset_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if dataset_row:
        base = json.loads(json.dumps(dataset_row))  # deep copy
        hit = True
    else:
        base = {
            "transaction": build_mock_transaction(req),
            "customer": {},
            "external_services": build_mock_external_services(req),
            "risk": {},
            "features": {},
        }
        hit = False

    # Overlay request identity into customer
    base.setdefault("customer", {})
    base["customer"].update({
        "first_name": req.data.first_name,
        "last_name": req.data.last_name,
        "email": str(req.data.email),
        "phone": req.data.phone,
        "addresses": {
            "billing": (req.data.billing_address.model_dump() if req.data.billing_address else {
                "city": req.data.city,
                "state": req.data.state,
                "zip": req.data.zip,
                "country": "US",
            }),
            "shipping": (req.data.shipping_address.model_dump() if req.data.shipping_address else None),
        },
        "device": (req.data.device.model_dump() if req.data.device else None),
    })

    # Ensure external services exist
    base.setdefault("external_services", {})
    missing_any = any(k not in base["external_services"] for k in ["emailage", "threatmetrix", "ekata"])
    if missing_any:
        base["external_services"].update(build_mock_external_services(req))

    # Risk summary
    email_score = int(base["external_services"]["emailage"].get("score", 0))
    tm_score = int(base["external_services"]["threatmetrix"].get("risk_score", 0))
    blended = int(round((0.55 * tm_score) + (0.45 * email_score)))

    base["risk"] = {
        "blended_score": blended,
        "reason_codes": [
            "IP_PROXY" if base.get("transaction", {}).get("network", {}).get("ip_proxy") else None,
            "DISPOSABLE_EMAIL" if base["external_services"]["emailage"].get("disposable") else None,
            "BOT_DETECTED" if base["external_services"]["threatmetrix"].get("bot_detected") else None,
        ],
        "recommended_action": "REVIEW" if blended >= 60 else "ALLOW",
    }
    base["risk"]["reason_codes"] = [x for x in base["risk"]["reason_codes"] if x]

    return {
        "request_id": req.request_id,
        "transaction_id": req.transaction_id,
        "transaction_time": req.transaction_time.astimezone(timezone.utc).isoformat(),
        "dataset_hit": hit,
        "data": {
            "first_name": req.data.first_name,
            "last_name": req.data.last_name,
            "email": str(req.data.email),
            "ip": req.data.ip,
            "phone": req.data.phone,
            "city": req.data.city,
            "state": req.data.state,
            "zip": req.data.zip,
        },
        "transaction_payload": base,
    }


def enrich_with_emailage(req: EnrichRequest, dataset_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Enrich transaction with Emailage data only"""
    if dataset_row and "external_services" in dataset_row and "emailage" in dataset_row["external_services"]:
        emailage_data = dataset_row["external_services"]["emailage"]
        dataset_hit = True
    else:
        emailage_data = build_mock_emailage(req)
        dataset_hit = False

    return {
        "request_id": req.request_id,
        "transaction_id": req.transaction_id,
        "transaction_time": req.transaction_time.astimezone(timezone.utc).isoformat(),
        "dataset_hit": dataset_hit,
        "service": "emailage",
        "data": {
            "first_name": req.data.first_name,
            "last_name": req.data.last_name,
            "email": str(req.data.email),
            "ip": req.data.ip,
            "phone": req.data.phone,
        },
        "enrichment": emailage_data
    }


def enrich_with_threatmetrix(req: EnrichRequest, dataset_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Enrich transaction with ThreatMetrix data only"""
    if dataset_row and "external_services" in dataset_row and "threatmetrix" in dataset_row["external_services"]:
        threatmetrix_data = dataset_row["external_services"]["threatmetrix"]
        dataset_hit = True
    else:
        threatmetrix_data = build_mock_threatmetrix(req)
        dataset_hit = False

    return {
        "request_id": req.request_id,
        "transaction_id": req.transaction_id,
        "transaction_time": req.transaction_time.astimezone(timezone.utc).isoformat(),
        "dataset_hit": dataset_hit,
        "service": "threatmetrix",
        "data": {
            "first_name": req.data.first_name,
            "last_name": req.data.last_name,
            "email": str(req.data.email),
            "ip": req.data.ip,
            "phone": req.data.phone,
        },
        "enrichment": threatmetrix_data
    }


def enrich_with_ekata(req: EnrichRequest, dataset_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Enrich transaction with Ekata data only"""
    if dataset_row and "external_services" in dataset_row and "ekata" in dataset_row["external_services"]:
        ekata_data = dataset_row["external_services"]["ekata"]
        dataset_hit = True
    else:
        ekata_data = build_mock_ekata(req)
        dataset_hit = False

    return {
        "request_id": req.request_id,
        "transaction_id": req.transaction_id,
        "transaction_time": req.transaction_time.astimezone(timezone.utc).isoformat(),
        "dataset_hit": dataset_hit,
        "service": "ekata",
        "data": {
            "first_name": req.data.first_name,
            "last_name": req.data.last_name,
            "email": str(req.data.email),
            "ip": req.data.ip,
            "phone": req.data.phone,
        },
        "enrichment": ekata_data
    }
