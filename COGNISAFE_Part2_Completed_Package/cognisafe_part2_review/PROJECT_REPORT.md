# COGNISAFE — Part 2: Application Development and Integration

## 1. Project overview
COGNISAFE is a fraud/phishing-analysis application. The application layer accepts a message or URL, sends it to a FastAPI backend, and returns a risk score, risk category, detected reasons, and a recommendation for the user.

## 2. Work completed in this package
- FastAPI application with health-check and analysis routes.
- Message-analysis and URL-analysis endpoints.
- Pydantic request validation for empty/oversized messages and URL format.
- HTML, CSS, and JavaScript frontend files retained from the existing project.
- Automated API tests for health status, response fields, comparative message scoring, input validation, legitimate URL handling, and a brand-impersonation pattern.
- Setup instructions and a manual integration checklist.

## 3. Architecture
1. User selects message analysis or URL analysis in the browser.
2. The JavaScript frontend sends a JSON request to the FastAPI endpoint.
3. FastAPI validates the request.
4. The current placeholder detector applies rules and calculates a risk score.
5. The API returns a structured response.
6. The frontend displays the score, risk category, reasons, and recommendation.

## 4. API contract

### Health check
- Method: `GET`
- Route: `/health`

### Analyze a message
- Method: `POST`
- Route: `/api/v1/analyze/message`
- JSON body: `{"text": "message to analyze"}`

### Analyze a URL
- Method: `POST`
- Route: `/api/v1/analyze/url`
- JSON body: `{"url": "https://example.com"}`

Analysis responses include fields such as `risk_score`, `risk_level`, `reasons`, and `recommendation`. The existing implementation identifies its current detection method as rule-based.

## 5. Testing
The initial automated test suite contains eight tests. The test suite was executed in a Python environment during package preparation and returned:

`8 passed`

The user also ran the same tests locally and shared a screenshot showing `8 passed, 1 warning`. The warning concerns a Starlette TestClient/httpx deprecation notice; it did not fail the tests.

## 6. Important limitation
The detector currently in `main.py` is rule-based. It must not be presented as the teammate's trained AI model. Real model integration remains pending until the teammate's engine/interface is available and connected.

A low risk score is not proof that a message or URL is safe. The application should not automatically open or visit a suspicious URL.

## 7. Recommended next integration steps
1. Agree with the AI-engine teammate on the Python function/module to call and its input/output schema.
2. Keep the API response contract stable while swapping the placeholder detector for the actual engine.
3. Add tests for the real engine's normal, suspicious, malformed, and failure cases.
4. Run the manual checklist in `MANUAL_TEST_CHECKLIST.md`.
5. Record the final test results and any limitations in the submission/demo.
