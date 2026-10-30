import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from risk_scoring import analyze_message

project_folder = Path(__file__).resolve().parent.parent
data_file = project_folder / "data" / "fresh_messages.txt"

rows = []
with open(data_file, encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            print(f"Line {number} skipped: no | found")
            continue
        label, text = line.split("|", 1)
        label = label.strip().lower()
        if label not in ("scam", "ok"):
            print(f"Line {number} skipped: label must be scam or ok")
            continue
        rows.append((label, text.strip()))

n_scam = sum(1 for label, _ in rows if label == "scam")
n_ok = len(rows) - n_scam
print(f"Loaded {len(rows)} messages: {n_scam} scam, {n_ok} legitimate")
if n_scam < 20 or n_ok < 20:
    print("WARNING: fewer than 20 of one kind. Results will be very unreliable.")

levels = {"scam": {"Low": 0, "Medium": 0, "High": 0},
          "ok": {"Low": 0, "Medium": 0, "High": 0}}
missed = []
false_alarms = []

for label, text in rows:
    result = analyze_message(text)
    if "error" in result:
        print("Error for:", text[:50], "->", result["error"])
        continue
    level = result["risk_level"]
    levels[label][level] += 1
    flagged = level in ("Medium", "High")
    if label == "scam" and not flagged:
        missed.append((text, result))
    if label == "ok" and flagged:
        false_alarms.append((text, result))

tp = n_scam - len(missed)
fp = len(false_alarms)
print()
print("Risk levels given (flagged = Medium or High):")
print("                 Low   Medium   High")
for label, name in (("scam", "real scams     "), ("ok", "legitimate     ")):
    c = levels[label]
    print(f"{name}  {c['Low']:3d}   {c['Medium']:5d}   {c['High']:4d}")

print()
print(f"Scams missed (false negatives): {len(missed)} of {n_scam}")
print(f"Legitimate flagged (false positives): {fp} of {n_ok}")
if n_scam:
    print(f"Recall (scams caught): {tp / n_scam:.2f}")
if tp + fp:
    print(f"Precision (flags that were scams): {tp / (tp + fp):.2f}")

for title, items in (("MISSED SCAMS", missed), ("FALSE ALARMS", false_alarms)):
    print()
    print(f"--- {title} ---")
    for text, result in items:
        print(f"[score {result['risk_score']}] {text[:90]}")
        print("   details:", result["details"])