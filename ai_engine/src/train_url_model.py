from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Reuse the feature extractor you already wrote
from url_detector import extract_features

project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data" / "phiusiil"
csv_file = list(data_folder.rglob("*.csv"))[0]

# Read ONLY the URL text and the label (ignore the webpage-code columns)
df = pd.read_csv(csv_file, usecols=lambda c: c.lower() in ("url", "label"))
df.columns = [c.lower() for c in df.columns]

# Remove duplicate URLs so the same URL can't be in both train and test
before = len(df)
df = df.drop_duplicates(subset="url")
print("Rows:", before, "-> after removing duplicate URLs:", len(df))

# Turn each URL into features (text only, nothing is opened)
print("Extracting features... this can take a minute or two.")
rows = []
targets = []
for url, label in zip(df["url"], df["label"]):
    features = extract_features(str(url))
    if features is None:
        continue
    rows.append(features)
    # Dataset: 1 = legitimate, 0 = phishing.  Ours: 1 = phishing, 0 = legitimate
    targets.append(1 if label == 0 else 0)

X = pd.DataFrame(rows).astype(int)
y = pd.Series(targets)
feature_names = list(X.columns)
print("URLs used:", len(X), " phishing:", int(y.sum()), " legitimate:", int((y == 0).sum()))

# Split before training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train
model = RandomForestClassifier(
    n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced"
)
model.fit(X_train, y_train)

# Evaluate on unseen test URLs
predictions = model.predict(X_test)
print()
print("=== Classification report ===")
print(classification_report(y_test, predictions, target_names=["legitimate", "phishing"]))
print("=== Confusion matrix ===")
cm = confusion_matrix(y_test, predictions)
print("                   predicted legit   predicted phishing")
print("actual legitimate ", cm[0][0], "            ", cm[0][1])
print("actual phishing   ", cm[1][0], "            ", cm[1][1])

# Which features did the model rely on most?
print()
print("=== Feature importance (higher = used more) ===")
ranked = sorted(zip(feature_names, model.feature_importances_), key=lambda p: -p[1])
for name, value in ranked:
    print(f"  {name}: {value:.3f}")

# Save the model together with the feature order it expects
models_folder = project_folder / "models"
models_folder.mkdir(exist_ok=True)
model_file = models_folder / "url_model.joblib"
joblib.dump({"model": model, "feature_names": feature_names}, model_file)
print()
print("Model saved to:", model_file)

# Quick sanity check on a few made-up URLs (text only, never opened)
print()
print("=== Sanity check ===")
samples = [
    "https://www.wikipedia.org/",
    "http://192.168.1.1/login/verify-account",
    "http://secure-update-account.example.net/login@verify",
]
for sample in samples:
    f = extract_features(sample)
    row = pd.DataFrame([f])[feature_names].astype(int)
    score = model.predict_proba(row)[0][1] * 100
    print(f"score {score:5.1f}  ->  {sample}")