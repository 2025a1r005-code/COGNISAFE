from pathlib import Path
import joblib

MODEL_DIR = Path(__file__).parent / "models"
_message_model = None


def _load_message_model():
    global _message_model
    if _message_model is None:
        _message_model = joblib.load(MODEL_DIR / "message_model.joblib")
    return _message_model


def predict_message_spam_probability(text: str) -> float:
    """Return the model's spam probability (0.0 to 1.0) for one message."""
    model = _load_message_model()
    spam_index = list(model.classes_).index("spam")
    return float(model.predict_proba([text])[0][spam_index])
