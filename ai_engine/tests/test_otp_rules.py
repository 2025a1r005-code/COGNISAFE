import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from risk_scoring import analyze_message

OTP_REASON = "OTP, PIN or password"


def test_genuine_otp_alert_has_no_otp_warning():
    result = analyze_message("Your OTP for login is 482913. Do not share it with anyone.")
    assert not any(OTP_REASON in reason for reason in result["reasons"])


def test_asking_for_otp_is_flagged():
    result = analyze_message("Please share the OTP you just received to cancel the fraud transaction")
    assert any(OTP_REASON in reason for reason in result["reasons"])