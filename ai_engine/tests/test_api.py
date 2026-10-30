import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

SUCCESS_FIELDS = ["risk_score", "risk_level", "category", "reasons",
                  "recommendation", "limitations"]


def check_success(response):
    assert response.status_code == 200
    body = response.json()
    for field in SUCCESS_FIELDS:
        assert field in body
    assert 0 <= body["risk_score"] <= 100
    assert body["risk_level"] in ("Low", "Medium", "High")
    assert len(body["reasons"]) >= 1
    assert "not a probability" in body["limitations"]


def check_error(response):
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_input"
    assert isinstance(body["error"]["message"], str)
    assert "risk_score" not in body


# ---------- /health ----------

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["models_loaded"] is True


# ---------- successful calls ----------

def test_message_success():
    check_success(client.post("/api/v1/analyze/message",
                              json={"text": "Your KYC is pending, update now: bit.ly/abc"}))


def test_url_success():
    check_success(client.post("/api/v1/analyze/url",
                              json={"url": "http://192.168.1.1/login/verify-account"}))


# ---------- bad input must give the agreed 400 error ----------

@pytest.mark.parametrize("body", [
    {"text": ""},            # empty
    {"text": "   "},         # only spaces
    {"text": 123},           # not a string
    {"text": None},          # null
    {},                      # field missing
    {"wrong_field": "hi"},   # wrong field name
    {"text": "x" * 6000},    # too long
])
def test_message_bad_input(body):
    check_error(client.post("/api/v1/analyze/message", json=body))


@pytest.mark.parametrize("body", [
    {"url": ""},
    {"url": 123},
    {},
    {"url": "http://[bad-url"},
    {"url": "x" * 6000},
])
def test_url_bad_input(body):
    check_error(client.post("/api/v1/analyze/url", json=body))


def test_body_that_is_not_json():
    response = client.post(
        "/api/v1/analyze/message",
        content="this is not json",
        headers={"Content-Type": "application/json"},
    )
    check_error(response)