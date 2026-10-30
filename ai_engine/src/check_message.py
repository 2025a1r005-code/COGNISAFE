from pathlib import Path
import joblib

project_folder = Path(__file__).resolve().parent.parent
model_file = project_folder / "models" / "message_model.joblib"

pipeline = joblib.load(model_file)
spam_position = list(pipeline.classes_).index("spam")

print("COGNISAFE message checker (learning prototype)")
print("Type a message and press Enter. Type quit to stop.")

while True:
    text = input("\nMessage: ").strip()
    if text.lower() == "quit":
        break
    if not text:
        print("Please type a message first.")
        continue

    score = pipeline.predict_proba([text])[0][spam_position] * 100
    label = pipeline.predict([text])[0]

    print("Model label:", label)
    print("Model score (0-100):", round(score))
    print("Note: this score is NOT a probability of fraud.")
    print("A low score does not mean the message is safe.")