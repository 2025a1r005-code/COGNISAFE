from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split

from url_detector import extract_features

project_folder = Path(__file__).resolve().parent.parent
csv_file = list((project_folder / "data" / "phiusiil").rglob("*.csv"))[0]
output_file = project_folder / "models" / "url_calibrated.joblib"

# Same loading steps as train_url_model.py
df = pd.read_csv(csv_file, usecols=lambda c: c.lower() in ("url", "label"))
df.columns = [c.lower() for c in df.columns]
df = df.drop_duplicates(subset="url")

rows, targets = [], []
for url, label in zip(df["url"], df["label"]):
    features = extract_features(str(url))
    if features is None:
        continue
    rows.append(features)
    targets.append(1 if label == 0 else 0)  # 1 = phishing

X = pd.DataFrame(rows).astype(int)
y = pd.Series(targets)
feature_names = list(X.columns)

# 60% train the model, 20% teach the calibrator, 20% final test
X_rest, X_test, y_rest, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
X_fit, X_cal, y_fit, y_cal = train_test_split(
    X_rest, y_rest, test_size=0.25, random_state=42, stratify=y_rest)

print("Model-training URLs:", len(X_fit))
print("Calibration URLs:   ", len(X_cal))
print("Test URLs:          ", len(X_test))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


model = RandomForestClassifier(
    n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced")
model.fit(X_fit, y_fit)

raw_cal = model.predict_proba(X_cal)[:, 1]
platt = LogisticRegression().fit(logit(raw_cal), y_cal)

raw_test = model.predict_proba(X_test)[:, 1]
platt_test = platt.predict_proba(logit(raw_test))[:, 1]

raw_brier = brier_score_loss(y_test, raw_test)
cal_brier = brier_score_loss(y_test, platt_test)
print()
print("Brier score on unseen test URLs (lower is better)")
print("  raw Random Forest:", round(raw_brier, 4))
print("  Platt calibrated :", round(cal_brier, 4))

# Reliability table for the calibrated numbers
print()
print("Reliability table (calibrated)")
print("  predicted range   URLs    avg predicted   actual phishing share")
edges = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0000001]
actual = np.asarray(y_test)
for low, high in zip(edges[:-1], edges[1:]):
    mask = (platt_test >= low) & (platt_test < high)
    count = int(mask.sum())
    if count == 0:
        print(f"  {low:.1f} - {min(high, 1.0):.1f}        {0:6d}")
        continue
    print(f"  {low:.1f} - {min(high, 1.0):.1f}        {count:6d}      "
          f"{platt_test[mask].mean():.2f}            {actual[mask].mean():.2f}")

if cal_brier < raw_brier:
    joblib.dump({"model": model, "platt": platt, "feature_names": feature_names}, output_file)
    print()
    print("Calibration helped. Saved:", output_file)
else:
    print()
    if output_file.exists():
        print("Calibration did NOT help this time. The older file at", output_file,
              "is still there. Delete it yourself if you want the extra field to stop appearing.")
    else:
        print("Calibration did NOT help, so nothing was saved. Your scorer is unchanged.")