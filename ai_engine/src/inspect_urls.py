from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data" / "phiusiil"

# Find the CSV file inside the extracted folder
csv_files = list(data_folder.rglob("*.csv"))
if not csv_files:
    print("No CSV file found in:", data_folder)
    raise SystemExit

csv_file = csv_files[0]
print("Reading:", csv_file.name)

df = pd.read_csv(csv_file)
print("Rows and columns:", df.shape)
print()
print("First 10 column names:", list(df.columns[:10]))
print("Last 5 column names:", list(df.columns[-5:]))

# Find the label column without assuming its exact spelling
label_columns = [c for c in df.columns if c.lower() == "label"]
if not label_columns:
    print("Could not find a 'label' column. Check the column names above.")
    raise SystemExit

label_col = label_columns[0]
print()
print("Label counts (1 = legitimate, 0 = phishing):")
print(df[label_col].value_counts())

# Show a few URLs as plain text. Do NOT click or open them.
print()
print("--- 3 legitimate URLs (text only, do not open) ---")
for url in df[df[label_col] == 1]["URL"].head(3):
    print(" ", str(url)[:80])

print()
print("--- 3 phishing URLs (text only, do NOT click or open) ---")
for url in df[df[label_col] == 0]["URL"].head(3):
    print(" ", str(url)[:80])