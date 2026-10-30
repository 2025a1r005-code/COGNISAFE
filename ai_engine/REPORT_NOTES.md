# COGNISAFE - report notes (fill in YOUR numbers from YOUR runs)

## 1. What was built
- Message analyzer: CountVectorizer + Multinomial Naive Bayes, trained on the SMS Spam Collection (5,574 messages, ham/spam).
- URL analyzer: 10 hand-written URL features (length, HTTPS, IP host, dots/hyphens in host, digits, @ symbol, punycode, shortener, suspicious words) + Random Forest, trained on the URL column of the PhiUSIIL dataset.
- Risk scoring: 70% model score + warning-sign points (max 40), capped at 100. Levels: Low <30, Medium 30-69, High 70+. Weights and thresholds were chosen by hand and NOT tuned or validated.
- Local API (FastAPI) following a DRAFT contract agreed with the app developer: POST /api/v1/analyze/message, POST /api/v1/analyze/url, GET /health.
- URLs are only read as text. No URL is ever opened or fetched.

## 2. Evaluation 1 - held-out test split of the SMS dataset
- Split: 80% train / 20% test, stratified, random_state=42, split BEFORE vectorizing (no leakage).
- Test messages: ____  (ham ____, spam ____)
- Spam precision: ____   Spam recall: ____   Spam F1: ____
- Confusion matrix: ham->ham ____, ham->spam ____, spam->ham ____, spam->spam ____
- Caveat: about 87% of messages are ham, so overall accuracy alone is misleading. Report precision and recall.

## 3. Evaluation 2 - held-out test split of the PhiUSIIL URL dataset
- Duplicate URLs removed before splitting. Test URLs: ____
- Phishing precision: ____   Phishing recall: ____   F1: ____
- Confusion matrix: legit->legit ____, legit->phishing ____, phishing->legit ____, phishing->phishing ____
- Caveat: this dataset's legitimate and phishing URLs may differ in style, so high scores may not carry over to real attacks.

## 4. Evaluation 3 - fresh messages (collected AFTER the rules were written)
- Source: messages collected from ____ with permission, personal details removed.
- Size: ____ scams, ____ legitimate. (State plainly that this is a small sample.)
- Scams missed (false negatives): ____ of ____
- Legitimate flagged (false positives): ____ of ____
- Typical mistakes observed: ____
- This is the most realistic result of the three. Report it first or give it equal weight.

## 5. Things NOT proven
- Not tested on live, real-time scam traffic.
- Message model trained on old UK/Singapore SMS data; may miss current regional scam styles.
- Risk score is NOT a calibrated probability.
- Low score does NOT mean safe.
- No protection against scammers who deliberately imitate genuine wording.
- API has no authentication, rate limiting or privacy review. Not production-ready.

## 6. Possible future work
- Collect a larger, labelled, region-relevant message dataset (with consent and licensing checked).
- Calibrate the scores (for example with CalibratedClassifierCV) before ever calling them probabilities.
- Evaluate URL detection on fresh URLs from a different source than the training dataset.
- Add authentication, rate limiting and logging policy before any real deployment.

## 7. Credits
See README.md for dataset citations and licenses (both CC BY 4.0).