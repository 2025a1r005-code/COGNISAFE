import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from risk_scoring import analyze_message, analyze_url

# (text, is_suspicious)
MESSAGES = [
    ("Dear customer, your KYC is pending. Update now or your account will be blocked: bit.ly/kyc-update", True),
    ("Your bank account has been suspended. Verify your details immediately at http://secure-bank-login.example.net", True),
    ("Congratulations! You have won a Rs 50,000 lottery. Send your OTP to claim the prize", True),
    ("URGENT: Your electricity will be disconnected tonight. Call the number below now to avoid cut-off", True),
    ("You have a pending refund of Rs 4,999. Click the link to receive it: tinyurl.com/refund-now", True),
    ("Your parcel is held at customs. Pay a small fee to release it: http://track-parcel.example.org", True),
    ("Hi, I am from the bank security team. Please share the OTP you just received to cancel the fraud transaction", True),
    ("Earn Rs 5,000 daily from home! No experience needed. Message us now to join", True),
    ("Your SIM will be deactivated in 24 hours. Complete your KYC at www.sim-verify.example.com", True),
    ("Final notice: your card has been blocked. Update your PIN now to restore access", True),

    ("Are you coming to the library after class?", False),
    ("Your OTP for login is 482913. Do not share it with anyone.", False),
    ("Your order #4521 has been shipped and will arrive on Friday.", False),
    ("Reminder: your dentist appointment is tomorrow at 10 AM.", False),
    ("Hi, can you send me the notes from today's lecture?", False),
    ("Your electricity bill of Rs 1,240 has been paid. Thank you.", False),
    ("Happy birthday! Dinner at 8 tonight, don't be late", False),
    ("The project meeting has moved to 3 PM in room 204.", False),
    ("Rs 2,000 debited from your account at a grocery store. If this was not you, call the number on your card.", False),
    ("Your package was delivered to the front desk.", False),
]

URLS = [
    ("http://192.168.0.15/secure/login/verify", True),
    ("http://secure-login-update-account.example.net/verify", True),
    ("http://paypa1-account-verify.example.com/login", True),
    ("http://www.bank-kyc-update.example.org/otp/confirm", True),
    ("https://xn--pple-43d.example.com/account/login", True),
    ("http://login.verify-secure.example.net@192.0.2.10/account", True),
    ("http://secure.example.net.account-verify.example.org/password/confirm", True),
    ("http://update-your-bank-password.example.net/login", True),

    ("https://www.wikipedia.org/", False),
    ("https://www.google.com/", False),
    ("https://github.com/", False),
    ("https://www.python.org/downloads/", False),
    ("https://en.wikipedia.org/wiki/Machine_learning", False),
    ("https://www.bbc.com/news", False),
    ("https://docs.python.org/3/library/pathlib.html", False),
    ("http://www.example.com/about", False),
    ("https://accounts.google.com/signin", False),
]


def evaluate(title, items, analyze):
    print("=" * 70)
    print(title)
    print("=" * 70)
    tp = fp = fn = tn = 0
    mistakes = []

    for text, is_bad in items:
        result = analyze(text)
        if "error" in result:
            print("ERROR  ", text[:60], "->", result["error"])
            continue
        flagged = result["risk_level"] in ("Medium", "High")
        if is_bad and flagged:
            tp += 1
            verdict = "caught      "
        elif is_bad and not flagged:
            fn += 1
            verdict = "MISSED SCAM "
            mistakes.append(("missed scam", text, result))
        elif not is_bad and flagged:
            fp += 1
            verdict = "FALSE ALARM "
            mistakes.append(("false alarm", text, result))
        else:
            tn += 1
            verdict = "ok          "
        print(f"{verdict} score {result['risk_score']:3d} {result['risk_level']:6s} | {text[:55]}")

    print()
    print(f"Scams caught: {tp}   Scams missed (false negatives): {fn}")
    print(f"Legitimate OK: {tn}   False alarms (false positives): {fp}")
    if tp + fn:
        print(f"Recall (share of scams caught): {tp / (tp + fn):.2f}")
    if tp + fp:
        print(f"Precision (share of flags that were scams): {tp / (tp + fp):.2f}")

    if mistakes:
        print()
        print("--- Mistakes in detail ---")
        for kind, text, result in mistakes:
            print(f"[{kind}] {text}")
            print("   score:", result["risk_score"], "| details:", result["details"])
            for reason in result["reasons"]:
                print("   -", reason)
    print()


evaluate("MESSAGES", MESSAGES, analyze_message)
evaluate("URLS (text only, never opened)", URLS, analyze_url)