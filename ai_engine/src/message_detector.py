from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

project_folder = Path(__file__).resolve().parent.parent
data_file = project_folder / "data" / "SMSSpamCollection"

labels = []
texts = []

with open(data_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        label, text = line.split("\t", 1)
        labels.append(label)
        texts.append(text)

# Split FIRST, before any learning happens
train_texts, test_texts, train_labels, test_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# A pipeline bundles the two steps into one object:
# 1) turn text into word counts, 2) classify
pipeline = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("model", MultinomialNB()),
])

# Learns vocabulary and trains, using TRAINING messages only
pipeline.fit(train_texts, train_labels)

# Evaluate on the unseen test messages
predictions = pipeline.predict(test_texts)
print(classification_report(test_labels, predictions, labels=["ham", "spam"]))
print(confusion_matrix(test_labels, predictions, labels=["ham", "spam"]))

# Save the trained pipeline into the models folder
models_folder = project_folder / "models"
models_folder.mkdir(exist_ok=True)
model_file = models_folder / "message_model.joblib"
joblib.dump(pipeline, model_file)
print()
print("Model saved to:", model_file)
