# COGNISAFE API contract (DRAFT v0.1 - to be agreed with the app developer)

All requests and responses use JSON (UTF-8). The server never opens or fetches any URL it receives.

## POST /api/v1/analyze/message

Request:
```json
{ "text": "Dear customer, your KYC is pending..." }
```

Rules: `text` is required, must be a string, not empty, and at most 5000 characters.

## POST /api/v1/analyze/url

Request:
```json
{ "url": "http://example.net/login" }
```

Rules: `url` is required, must be a string, not empty, and at most 5000 characters.

## Success response (HTTP 200) for both endpoints

```json
{
  "risk_score": 78,
  "risk_level": "High",
  "category": "Likely scam or spam message",
  "reasons": ["The message contains a link.", "It uses urgent or threatening wording to pressure you."],
  "recommendation": "Do not click links, reply, or share any personal details...",
  "limitations": "This is a learning prototype. The score is a rough warning signal, not a probability of fraud. A low score does not mean something is safe."
}
```

- `risk_score`: whole number 0-100. NOT a probability of fraud.
- `risk_level`: "Low" (below 30), "Medium" (30-69), or "High" (70 or more).
- `reasons`: list of at least one plain-language sentence.
- The app must always display `limitations` (or equivalent wording) next to the result.
- A "Low" result must never be shown as "safe".

## Error response (HTTP 400)

```json
{ "error": { "code": "invalid_input", "message": "Input is empty." } }
```

## GET /health

```json
{ "status": "ok", "models_loaded": true, "version": "0.1.0" }
```

## Open questions to agree on

1. Should the app log submitted messages? (Default proposal: no, for privacy.)
2. Is a maximum of 5000 characters acceptable for the UI?
3. Does the app need an optional `details` field (model score, warning-sign points) for debugging?
4. How should the UI show the "Medium" level and the limitations text?
5. Does the app need a separate HTTP status for server errors (500) and timeouts?