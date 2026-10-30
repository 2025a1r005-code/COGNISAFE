from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint_returns_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "COGNISAFE"


def test_message_endpoint_returns_expected_fields():
    response = client.post(
        "/api/v1/analyze/message",
        json={"text": "Hi, are we still meeting at the library tomorrow?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["risk_score"] <= 100
    assert isinstance(data["risk_level"], str)
    assert isinstance(data["reasons"], list)
    assert isinstance(data["recommendation"], str)
    assert data["detection_method"] == "rule_based"


def test_suspicious_message_scores_higher_than_neutral_message():
    neutral = client.post(
        "/api/v1/analyze/message",
        json={"text": "Hi, are we still meeting at the library tomorrow?"},
    )
    suspicious = client.post(
        "/api/v1/analyze/message",
        json={
            "text": (
                "URGENT! Your bank account will be blocked immediately. "
                "Click https://paypal-login.example.com/verify to verify "
                "your account and update your password."
            )
        },
    )
    assert neutral.status_code == 200
    assert suspicious.status_code == 200
    assert suspicious.json()["risk_score"] > neutral.json()["risk_score"]


def test_message_rejects_empty_text():
    response = client.post("/api/v1/analyze/message", json={"text": ""})
    assert response.status_code == 422


def test_message_rejects_text_over_limit():
    response = client.post(
        "/api/v1/analyze/message",
        json={"text": "x" * 10001},
    )
    assert response.status_code == 422


def test_url_endpoint_accepts_legitimate_example_domain():
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "https://www.google.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 0
    assert data["risk_level"] == "No Risk Detected"
    assert isinstance(data["reasons"], list)


def test_url_endpoint_detects_brand_impersonation_pattern():
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "https://google.com.example.org/login"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 35
    assert any("brand impersonation" in reason.lower() for reason in data["reasons"])


def test_url_rejects_invalid_url():
    response = client.post(
        "/api/v1/analyze/url",
        json={"url": "not-a-valid-url"},
    )
    assert response.status_code == 422
