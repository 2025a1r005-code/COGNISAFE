import sys
from pathlib import Path

# Let the tests find the files inside src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from risk_scoring import analyze_message, analyze_url

REQUIRED_FIELDS = ["risk_score", "risk_level", "category", "reasons",
                   "recommendation", "limitations"]


# ---------- Bad input must give an error, never a crash ----------

@pytest.mark.parametrize("bad", ["", "   ", None, 123, "x" * 6000])
def test_message_bad_input_returns_error(bad):
    result = analyze_message(bad)
    assert "error" in result
    assert "risk_score" not in result


@pytest.mark.parametrize("bad", ["", "   ", None, 123, "http://[bad-url"])
def test_url_bad_input_returns_error(bad):
    result = analyze_url(bad)
    assert "error" in result
    assert "risk_score" not in result


# ---------- Every normal result has the agreed shape ----------

def check_shape(result):
    for field in REQUIRED_FIELDS:
        assert field in result
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in ("Low", "Medium", "High")
    assert len(result["reasons"]) >= 1
    assert "not a probability" in result["limitations"]


def test_message_result_shape():
    check_shape(analyze_message("Are you coming to the library after class?"))


def test_url_result_shape():
    check_shape(analyze_url("https://www.wikipedia.org/"))


# ---------- Suspicious examples should be flagged ----------

def test_fake_bank_otp_message_is_not_low():
    result = analyze_message(
        "URGENT: your account is blocked. Share your OTP at bit.ly/abc to unblock"
    )
    assert result["risk_level"] in ("Medium", "High")


def test_prize_message_is_not_low():
    result = analyze_message(
        "Congratulations! You won a free prize. Call now to claim your reward"
    )
    assert result["risk_level"] in ("Medium", "High")


def test_ip_address_login_url_gives_ip_reason():
    result = analyze_url("http://192.168.1.1/login/verify-account")
    assert any("IP" in reason for reason in result["reasons"])
    assert result["risk_score"] >= 25


# ---------- Ordinary examples should stay low ----------

def test_normal_chat_message_is_low():
    result = analyze_message("Are you coming to the library after class?")
    assert result["risk_level"] == "Low"


def test_wikipedia_is_low():
    result = analyze_url("https://www.wikipedia.org/")
    assert result["risk_level"] == "Low"


# ---------- Safety rules ----------

def test_low_result_never_promises_safety():
    result = analyze_message("Are you coming to the library after class?")
    text = (result["recommendation"] + " " + result["limitations"]).lower()
    assert "does not mean" in text or "limited" in text
    assert "100% safe" not in text