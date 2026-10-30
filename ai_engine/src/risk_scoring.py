import json
import re
from pathlib import Path

import joblib
import pandas as pd

from url_detector import extract_features

project_folder = Path(__file__).resolve().parent.parent

# Load the two saved models
message_pipeline = joblib.load(project_folder / "models" / "message_model.joblib")
url_bundle = joblib.load(project_folder / "models" / "url_model.joblib")
url_model = url_bundle["model"]
url_feature_names = url_bundle["feature_names"]
# Optional calibrated estimate. The file exists only if train_calibrated_message.py found an improvement.
import numpy as np
calibrated_file = project_folder / "models" / "message_calibrated.joblib"
calibrated_bundle = joblib.load(calibrated_file) if calibrated_file.exists() else None
url_calibrated_file = project_folder / "models" / "url_calibrated.joblib"
url_calibrated_bundle = joblib.load(url_calibrated_file) if url_calibrated_file.exists() else None


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)

MAX_LENGTH = 5000

LIMITATIONS = (
    "This is a learning prototype. The score is a rough warning signal, "
    "not a probability of fraud. A low score does not mean something is safe."
)

RECOMMENDATIONS = {
    "High": "Do not click links, reply, or share any personal details. "
            "Contact the organisation using a phone number or website you already trust.",
    "Medium": "Be careful. Do not click links or share OTPs, PINs or passwords. "
              "Check with the sender through an official channel first.",
    "Low": "No strong warning signs were found, but this check is limited. "
           "Stay careful with links and never share OTPs, PINs or passwords.",
}

# Phrases such as "do not share your OTP" are removed before we look for requests
NEGATED_SHARING = re.compile(
    r"\b(do not|don't|dont|never)\s+(share|disclose|give|tell|send)\b(\s+\w+){0,3}"
)
# Asking you to hand over a secret: "share the OTP", "update your PIN", ...
ASKS_FOR_SECRET = re.compile(
    r"\b(share|send|give|tell|provide|reply|forward|enter|submit|confirm|verify|update)\b"
    r"(\s+\w+){0,4}\s+(otp|pin|password|cvv)\b"
)
HAS_LINK = re.compile(r"(https?://|www\.|\b(bit\.ly|tinyurl\.com)/)")
URGENT = re.compile(
    r"\b(urgent|urgently|immediately|suspended|blocked|expires?|expired|last chance)\b"
)
PRIZE = re.compile(r"\b(won|winner|prize|lottery|reward|cashback|free gift)\b")
SCAM_THEME = re.compile(
    r"\b(kyc|refund|customs|disconnected|disconnection|deactivated|deactivation|"
    r"processing fee|small fee|pay a fee)\b"
)


def risk_level(score):
    if score >= 70:
        return "High"
    if score >= 30:
        return "Medium"
    return "Low"


def check_input(value):
    """Return an error message if the input is unusable, otherwise None."""
    if not isinstance(value, str):
        return "Input must be text."
    if not value.strip():
        return "Input is empty."
    if len(value) > MAX_LENGTH:
        return f"Input is too long (maximum {MAX_LENGTH} characters)."
    return None


def combine(model_score, bonus_points):
    """70% model score + warning-sign points (max 40), capped at 100."""
    bonus = min(40, bonus_points)
    return min(100, round(0.7 * model_score + bonus)), bonus


def build_result(score, model_score, bonus, reasons, categories):
    level = risk_level(score)
    if not reasons:
        reasons = ["No strong warning signs were found, but this check is limited."]
    return {
        "risk_score": score,
        "risk_level": level,
        "category": categories[level],
        "reasons": reasons,
        "recommendation": RECOMMENDATIONS[level],
        "details": {"model_score": round(model_score), "warning_sign_points": bonus},
        "limitations": LIMITATIONS,
    }


def analyze_message_base(text):
    error = check_input(text)
    if error:
        return {"error": error}
    text = text.strip()

    spam_position = list(message_pipeline.classes_).index("spam")
    model_score = message_pipeline.predict_proba([text])[0][spam_position] * 100

    lowered = text.lower()
    cleaned = NEGATED_SHARING.sub(" ", lowered)
    reasons = []
    points = 0

    if model_score >= 70:
        reasons.append("The message wording is similar to spam messages the model was trained on.")
    if HAS_LINK.search(lowered):
        reasons.append("The message contains a link.")
        points += 10
    if ASKS_FOR_SECRET.search(cleaned):
        reasons.append("It asks you to share or enter an OTP, PIN or password. Real services never ask for these.")
        points += 10
    if URGENT.search(lowered):
        reasons.append("It uses urgent or threatening wording to pressure you.")
        points += 10
    if PRIZE.search(lowered):
        reasons.append("It promises a prize or reward.")
        points += 10
    if SCAM_THEME.search(lowered):
        reasons.append("It mentions KYC, refunds, fees or service cut-offs, a common scam theme.")
        points += 10

    score, bonus = combine(model_score, points)
    categories = {
        "High": "Likely scam or spam message",
        "Medium": "Possibly suspicious message",
        "Low": "No strong warning signs found",
    }
    return build_result(score, model_score, bonus, reasons, categories)


def analyze_message(text):
    result = analyze_message_base(text)
    if "error" not in result and calibrated_bundle is not None:
        raw = calibrated_bundle["pipeline"].predict_proba([text.strip()])[0][1]
        estimate = calibrated_bundle["platt"].predict_proba(_logit(np.array([raw])))[0][1]
        result["details"]["calibrated_model_estimate"] = round(float(estimate) * 100)
        result["details"]["calibrated_model_estimate_note"] = (
            "Rough estimate for messages similar to an old SMS spam dataset only. "
            "It is not a probability of fraud."
        )
    return result

def analyze_url_base(url):
    error = check_input(url)
    if error:
        return {"error": error}

    features = extract_features(url)
    if features is None:
        return {"error": "Could not read this as a URL."}

    row = pd.DataFrame([features])[url_feature_names].astype(int)
    model_score = url_model.predict_proba(row)[0][1] * 100  # class 1 = phishing

    reasons = []
    points = 0

    if model_score >= 70:
        reasons.append("The URL pattern is similar to phishing URLs the model was trained on.")
    if features["host_is_ip"]:
        reasons.append("The address uses a raw IP number instead of a normal website name.")
        points += 10
    if features["has_at_symbol"]:
        reasons.append("The URL contains an @ symbol, which can hide the real destination.")
        points += 10
    if features["is_shortener"]:
        reasons.append("It is a shortened link, so the real destination is hidden.")
        points += 10
    if features["has_punycode"]:
        reasons.append("The website name has unusual characters (xn--) that can imitate a real site.")
        points += 10
    if features["suspicious_word_count"] >= 2:
        reasons.append("The URL contains several words often used in phishing (such as login or verify).")
        points += 10
    if not features["uses_https"]:
        reasons.append("The site does not use HTTPS. (Having HTTPS would not prove it is safe, though.)")
        points += 5

    score, bonus = combine(model_score, points)
    categories = {
        "High": "Likely phishing URL",
        "Medium": "Possibly suspicious URL",
        "Low": "No strong warning signs found",
    }
    return build_result(score, model_score, bonus, reasons, categories)

def analyze_url(url):
    result = analyze_url_base(url)
    if "error" not in result and url_calibrated_bundle is not None:
        features = extract_features(url)
        if features is not None:
            names = url_calibrated_bundle["feature_names"]
            row = pd.DataFrame([features])[names].astype(int)
            raw = url_calibrated_bundle["model"].predict_proba(row)[0][1]
            estimate = url_calibrated_bundle["platt"].predict_proba(
                _logit(np.array([raw])))[0][1]
            result["details"]["calibrated_model_estimate"] = round(float(estimate) * 100)
            result["details"]["calibrated_model_estimate_note"] = (
                "Rough estimate for URLs similar to one research dataset only. "
                "It is not a probability that a site is phishing."
            )
    return result


if __name__ == "__main__":
    print("=== MESSAGES ===")
    for message in [
        "Congratulations! You won a free prize. Call now to claim your reward",
        "URGENT: your account is blocked. Share your OTP at bit.ly/abc to unblock",
        "Your OTP for login is 482913. Do not share it with anyone.",
        "Are you coming to the library after class?",
        "",
    ]:
        print("\nINPUT:", repr(message))
        print(json.dumps(analyze_message(message), indent=2, ensure_ascii=False))

    print("\n\n=== URLS (text only, never opened) ===")
    for link in [
        "https://www.wikipedia.org/",
        "http://192.168.1.1/login/verify-account",
        "http://[bad-url",
    ]:
        print("\nINPUT:", repr(link))
        print(json.dumps(analyze_url(link), indent=2, ensure_ascii=False))