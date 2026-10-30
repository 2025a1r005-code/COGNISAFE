# COGNISAFE Manual Integration Checklist

## Start the app
- [ ] Activate the project's virtual environment.
- [ ] Start backend from the project root: `python -m uvicorn main:app --reload`
- [ ] Open `http://127.0.0.1:8000/health` and confirm a healthy response.
- [ ] In a second terminal, start frontend: `python -m http.server 5500 --directory frontend`
- [ ] Open `http://127.0.0.1:5500/`.

## Message analysis
- [ ] Submit a normal, harmless message.
- [ ] Submit a message that contains urgency, account-verification wording, and a suspicious link.
- [ ] Confirm the result area displays a score, risk category, reasons, and recommendation.
- [ ] Submit an empty message and confirm validation/error feedback appears rather than a broken page.
- [ ] Submit a long message and confirm the API rejects it cleanly.

## URL analysis
- [ ] Test `https://www.google.com` as a familiar legitimate example.
- [ ] Test `https://google.com.example.org/login` as a lookalike-host example.
- [ ] Test `http://127.0.0.1/login` as a local IP-host example.
- [ ] Test an invalid URL and confirm validation feedback.
- [ ] Do not click or automatically open suspicious URLs during testing.

## API and regression checks
- [ ] Open `http://127.0.0.1:8000/docs` and confirm both POST endpoints are listed.
- [ ] Run `python -m pytest -v`.
- [ ] Confirm all tests pass after any changes.
- [ ] Check the browser developer console for JavaScript errors and failed API requests.

## Before demo/submission
- [ ] State clearly that current scoring is rule-based unless the real AI engine has been integrated.
- [ ] Demonstrate one normal message, one suspicious message, one legitimate URL, and one suspicious-looking URL.
- [ ] Explain that a low score does not guarantee safety.
