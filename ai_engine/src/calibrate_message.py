from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

project_folder = Path(__file__).resolve().parent.parent
data_file = project_folder / "data" / "SMSSpamCollection"

texts = []
y = []  # 1 = spam, 0 = ham
with open(data_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        label, text = line.split("\t", 1)
        y.append(1 if label == "spam" else 0)
        texts.append(text)

# 80% / 20% first, then split the 80% into "fit" and "calibration" parts
rest_texts, test_texts, rest_y, test_y = train_test_split(
    texts, y, test_size=0.2, random_state=42, stratify=y)
fit_texts, cal_texts, fit_y, cal_y = train_test_split(
    rest_texts, rest_y, test_size=0.25, random_state=42, stratify=rest_y)

print("Model-training messages:", len(fit_texts))
print("Calibration messages:   ", len(cal_texts))
print("Test messages:          ", len(test_texts))

# 1) Train the model on the first part only
pipeline = Pipeline([("vectorizer", CountVectorizer()), ("model", MultinomialNB())])
pipeline.fit(fit_texts, fit_y)


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


# 2) Teach two calibrators using the calibration part (the model has not seen it)
raw_cal = pipeline.predict_proba(cal_texts)[:, 1]
platt = LogisticRegression().fit(logit(raw_cal), cal_y)               # smooth S-curve
isotonic = IsotonicRegression(out_of_bounds="clip").fit(raw_cal, cal_y)  # step-shaped

# 3) Compare everything on the test part
raw_test = pipeline.predict_proba(test_texts)[:, 1]
platt_test = platt.predict_proba(logit(raw_test))[:, 1]
iso_test = isotonic.predict(raw_test)

print()
print("Brier score on test messages (lower is better):")
print("  raw Naive Bayes :", round(brier_score_loss(test_y, raw_test), 4))
print("  Platt calibrated:", round(brier_score_loss(test_y, platt_test), 4))
print("  Isotonic        :", round(brier_score_loss(test_y, iso_test), 4))


def reliability(name, probs):
    print()
    print(f"Reliability table: {name}")
    print("  predicted range   messages   avg predicted   actual spam share")
    edges = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0000001]
    probs = np.asarray(probs)
    actual = np.asarray(test_y)
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (probs >= low) & (probs < high)
        count = int(mask.sum())
        if count == 0:
            print(f"  {low:.1f} - {min(high, 1.0):.1f}        {0:6d}")
            continue
        print(f"  {low:.1f} - {min(high, 1.0):.1f}        {count:6d}        "
              f"{probs[mask].mean():.2f}            {actual[mask].mean():.2f}")


reliability("raw Naive Bayes", raw_test)
reliability("Platt calibrated", platt_test)

# A few examples
examples = [
    "Congratulations! You won a free prize. Call now to claim your reward",
    "Are you coming to the library after class?",
    "Your KYC is pending, update now or your account will be blocked",
]
raw_ex = pipeline.predict_proba(examples)[:, 1]
platt_ex = platt.predict_proba(logit(raw_ex))[:, 1]
print()
print("Examples (raw -> calibrated):")
for text, r, c in zip(examples, raw_ex, platt_ex):
    print(f"  {r:.3f} -> {c:.3f}   {text[:60]}")