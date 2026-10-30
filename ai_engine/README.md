# COGNISAFE

An AI-assisted prototype that analyzes suspicious text messages and URLs and returns a risk score, risk level, category, reasons, and a recommended safe next step.

**Status: learning prototype. NOT production-ready and NOT a reliable fraud detector.**

## Important limitations

- The risk score (0-100) is a rough warning signal. It is **not** a calibrated probability of fraud.
- A low score **never** means a message or URL is safe.
- The message model was trained on an older SMS spam dataset (mostly UK and Singapore texts). It may miss scam styles common elsewhere or today.
- The URL model was trained on a dataset whose legitimate and phishing URLs may differ in style, so test scores can look better than real-world performance.
- The code only reads URLs as text. It never opens or visits any URL.
- Evaluation so far uses a small hand-written example list and a held-out test split. It has not been tested on fresh, real-world data.

## Project structure

```
COGNISAFE/
  src/
    message_detector.py   trains and saves the message model
    url_detector.py       extracts simple features from a URL (text only)
    train_url_model.py    trains and saves the URL model
    risk_scoring.py       combines models and warning signs into one result
    check_message.py      small command-line message checker
    inspect_urls.py       prints a summary of the URL dataset
  tests/
    test_risk_scoring.py  automated tests (pytest)
    evaluate_examples.py  counts false positives and false negatives
  API_CONTRACT.md         DRAFT API agreement with the app developer
  requirements.txt        Python packages used
```

The folders `data/`, `models/` and `.venv/` are not shared. Recreate them with the steps below.

## Setup (Windows, PowerShell)

1. Create and activate a virtual environment, then install packages:
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
2. Download the datasets listed under "Data sources" and place them in `data/`:
   - `data/SMSSpamCollection`
   - `data/phiusiil/` (the extracted CSV file)
3. Train the models:
   ```
   python src\message_detector.py
   python src\train_url_model.py
   ```
4. Try the scorer and run the tests:
   ```
   python src\risk_scoring.py
   python -m pytest tests -v
   python tests\evaluate_examples.py
   ```

## How the risk score works

Final score = 70% of the model's score + warning-sign points (up to 40), capped at 100.
Levels: Low below 30, Medium 30-69, High 70 or more.
The weights and thresholds were chosen by hand and have not been tuned or validated.

## Data sources and credits

- **SMS Spam Collection** - Almeida, T. A. and Hidalgo, J. M. G. UCI Machine Learning Repository. License: CC BY 4.0. https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- **PhiUSIIL Phishing URL Dataset** - Prasad, A. and Chandra, S. (2024). "PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning." Computers & Security. https://doi.org/10.1016/j.cose.2023.103545. UCI Machine Learning Repository, License: CC BY 4.0. https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

Only the URL text and label columns of the PhiUSIIL dataset are used. The page-content columns are ignored.

## API (proposed)

See `API_CONTRACT.md`. Endpoints proposed: `POST /api/v1/analyze/message`, `POST /api/v1/analyze/url`, `GET /health`. This is a draft and not final.