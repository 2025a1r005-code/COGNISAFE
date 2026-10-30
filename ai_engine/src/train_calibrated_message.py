from pathlib import Path
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

project_folder = Path(__file__).resolve().parent.parent
data_file = project_folder / "data" / "SMSSpamCollection"
output_file = project_folder / "models" / "message_calibrated.joblib"

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

# 60% train the model, 20% teach the calibrator, 20% final test
rest_texts, test_texts, rest_y, test_y = train_test_split(
    texts, y, test_size=0.2, random_state=42, stratify=y)
fit_texts, cal_texts, fit_y, cal_y = train_test_split(
    rest_texts, rest_y, test_size=0.25, random_state=42, stratify=rest_y)


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


pipeline = Pipeline([("vectorizer", CountVectorizer()), ("model", MultinomialNB())])
pipeline.fit(fit_texts, fit_y)

raw_cal = pipeline.predict_proba(cal_texts)[:, 1]
platt = LogisticRegression().fit(logit(raw_cal), cal_y)

raw_test = pipeline.predict_proba(test_texts)[:, 1]
platt_test = platt.predict_proba(logit(raw_test))[:, 1]

raw_brier = brier_score_loss(test_y, raw_test)
cal_brier = brier_score_loss(test_y, platt_test)
print("Brier score on unseen test messages (lower is better)")
print("  raw Naive Bayes :", round(raw_brier, 4))
print("  Platt calibrated:", round(cal_brier, 4))

if cal_brier < raw_brier:
    joblib.dump({"pipeline": pipeline, "platt": platt}, output_file)
    print()
    print("Calibration helped. Saved:", output_file)
else:
    if output_file.exists():
        print()
        print("Calibration did NOT help this time. The older file at", output_file,
              "is still there. Delete it yourself if you want the extra field to stop appearing.")
    else:
        print()
        print("Calibration did NOT help, so nothing was saved. Your scorer is unchanged.")