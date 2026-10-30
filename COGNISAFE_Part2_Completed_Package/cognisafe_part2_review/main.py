import ipaddress
import re
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl


app = FastAPI(
    title="COGNISAFE API",
    description="Backend API for the COGNISAFE fraud detection application",
    version="1.0.0",
)


# Allow the local HTML frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


# -------------------- REQUEST MODELS --------------------

class MessageRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10000,
        description="The suspicious message to analyze",
    )


class URLRequest(BaseModel):
    url: HttpUrl


# -------------------- COMMON HELPERS --------------------

def get_risk_level(score: int) -> str:
    """Return a consistent risk category for a score from 0 to 100."""

    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 30:
        return "Medium"
    elif score >= 10:
        return "Low"
    else:
        return "No Risk Detected"


def get_recommendation(score: int) -> str:
    if score >= 60:
        return (
            "High-risk indicators were detected. Do not click links or "
            "share passwords, OTPs, PINs, or payment information. "
            "Verify the sender through an official channel."
        )
    elif score >= 30:
        return (
            "Treat this carefully. Verify the sender and website "
            "independently before taking action."
        )
    elif score >= 10:
        return (
            "Some warning indicators were detected. Check the sender "
            "and destination carefully before proceeding."
        )
    else:
        return (
            "No major configured warning indicators were detected. "
            "This does not guarantee that the message or URL is safe."
        )


# -------------------- MESSAGE FRAUD DETECTION --------------------

def detect_message_fraud(text: str) -> dict:
    """Analyze message text using transparent rule-based indicators."""

    message = text.lower()
    reasons = []
    score = 0

    # 1. Urgent or threatening language
    urgency_words = [
        "urgent",
        "immediately",
        "act now",
        "account blocked",
        "account suspended",
        "will be blocked",
        "expires today",
        "final warning",
        "within 24 hours",
        "suspended today",
    ]

    found_urgency = [
        word for word in urgency_words if word in message
    ]

    if found_urgency:
        score += 15
        reasons.append(
            "Urgent or threatening language detected: "
            + ", ".join(found_urgency[:4])
            + "."
        )

    # 2. Requests or references involving sensitive information
    sensitive_words = [
        "otp",
        "one-time password",
        "password",
        "pin",
        "cvv",
        "bank details",
        "credit card details",
        "card number",
        "security code",
    ]

    found_sensitive = [
        word for word in sensitive_words if word in message
    ]

    if found_sensitive:
        score += 25
        reasons.append(
            "Sensitive information is mentioned: "
            + ", ".join(found_sensitive[:4])
            + "."
        )

    # 3. Prize and reward scams
    reward_patterns = [
        r"\byou have won\b",
        r"\bclaim your prize\b",
        r"\bfree reward\b",
        r"\blottery winner\b",
        r"\bcongratulations.{0,60}\bwon\b",
        r"\bclaim your reward\b",
        r"\bwon a prize\b",
    ]

    if any(re.search(pattern, message) for pattern in reward_patterns):
        score += 20
        reasons.append(
            "Possible prize or reward scam language detected."
        )

    # 4. Extract links from the message
    urls = re.findall(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.IGNORECASE,
    )

    has_link = bool(urls)

    if has_link:
        score += 5
        reasons.append(
            "The message contains a link. Verify its destination "
            "before opening it."
        )

    # Check suspicious URL characteristics
    for raw_url in urls:
        parsed = urlparse(raw_url.rstrip(".,!?;:)"))
        hostname = (parsed.hostname or "").lower()

        if not hostname:
            continue

        # Internationalized/punycode domain
        if any(
            label.startswith("xn--")
            for label in hostname.split(".")
        ):
            score += 20
            reasons.append(
                "The link contains an internationalized domain label."
            )

        # IP address used as the hostname
        try:
            ipaddress.ip_address(hostname)
            score += 20
            reasons.append(
                "The link uses an IP address instead of a domain name."
            )
        except ValueError:
            pass

        if hostname.count("-") >= 3:
            score += 10
            reasons.append(
                "The link's hostname contains multiple hyphens."
            )

    # 5. Account-related language combined with an action request
    account_words = [
        "bank",
        "account",
        "payment",
        "wallet",
        "credit card",
        "debit card",
    ]

    action_words = [
        "verify",
        "confirm",
        "update",
        "login",
        "log in",
        "click",
        "validate",
        "unlock",
        "restore access",
    ]

    has_account_context = any(
        word in message for word in account_words
    )

    has_action_request = any(
        word in message for word in action_words
    )

    account_action = has_account_context and has_action_request

    if account_action:
        score += 15
        reasons.append(
            "Account-related language is combined with a request "
            "to click, log in, update, or verify information."
        )

    # 6. Additional risk when multiple warning signs occur together
    if found_urgency and has_link and account_action:
        score += 25
        reasons.append(
            "Multiple warning signs occur together: urgency, "
            "a link, and an account-related action request."
        )

    score = min(score, 100)
    risk_level = get_risk_level(score)

    if not reasons:
        reasons.append(
            "No configured message fraud indicators were detected."
        )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "category": "Message Analysis",
        "reasons": reasons,
        "recommendation": get_recommendation(score),
        "is_mock": False,
        "detection_method": "rule_based",
    }


# -------------------- URL FRAUD DETECTION --------------------

def detect_url_fraud(url: str) -> dict:
    """Analyze a URL using rule-based suspicious URL indicators."""

    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()

    score = 0
    reasons = []

    # 1. IP address instead of a domain name
    try:
        ipaddress.ip_address(hostname)
        score += 25
        reasons.append(
            "URL uses an IP address instead of a domain name."
        )
    except ValueError:
        pass

    # 2. Internationalized/punycode domain
    if any(
        label.startswith("xn--")
        for label in hostname.split(".")
    ):
        score += 25
        reasons.append(
            "URL contains an internationalized domain label."
        )

    # 3. Multiple hyphens in hostname
    if hostname.count("-") >= 3:
        score += 10
        reasons.append(
            "URL domain contains multiple hyphens."
        )

    # 4. Suspicious brand impersonation
    brand_domains = {
        "paypal": ["paypal.com"],
        "google": ["google.com"],
        "amazon": ["amazon.com", "amazon.in"],
        "microsoft": ["microsoft.com"],
        "apple": ["apple.com"],
        "sbi": ["sbi.co.in", "onlinesbi.sbi"],
    }

    for brand, legitimate_domains in brand_domains.items():
        if brand not in hostname:
            continue

        is_legitimate_domain = any(
            hostname == domain
            or hostname.endswith("." + domain)
            for domain in legitimate_domains
        )

        if not is_legitimate_domain:
            score += 35
            reasons.append(
                f"Possible brand impersonation detected: {brand}."
            )
            break

    # 5. URL contains credentials before the hostname
    if parsed.username is not None or parsed.password is not None:
        score += 20
        reasons.append(
            "URL contains user information before the hostname, "
            "which can be used to disguise the actual destination."
        )

    score = max(0, min(score, 100))
    risk_level = get_risk_level(score)

    if not reasons:
        reasons.append(
            "No configured URL fraud indicators were detected."
        )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "category": "URL Analysis",
        "reasons": reasons,
        "recommendation": get_recommendation(score),
        "is_mock": False,
        "detection_method": "rule_based_url",
    }


# -------------------- API ENDPOINTS --------------------

@app.get("/")
def root():
    return {
        "application": "COGNISAFE",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "COGNISAFE",
        "mode": "development",
    }


@app.post("/api/v1/analyze/message")
def analyze_message(request: MessageRequest):
    return detect_message_fraud(request.text)


@app.post("/api/v1/analyze/url")
def analyze_url(request: URLRequest):
    return detect_url_fraud(str(request.url))
