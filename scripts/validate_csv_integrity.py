"""Structural integrity check for the public survey CSVs.

Verifies row counts, column counts, ResponseId alignment between the
VALUES and LABELS exports, and a few representative value-vs-label
spot-checks for multi-select and rank-order questions.
"""
import csv
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VALUES_PATH = DATA_DIR / "survey_values.csv"
LABELS_PATH = DATA_DIR / "survey_labels.csv"

EXPECTED_RESPONDENTS = 27

print("=" * 70)
print("CSV STRUCTURAL INTEGRITY CHECK")
print("=" * 70)

print("\n--- 1. Raw CSV row counts (Python csv module) ---")
for label, path in [("VALUES", VALUES_PATH), ("LABELS", LABELS_PATH)]:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    print(f"  {label}: {len(rows)} total rows")
    print(f"    Row 0 (header):    {len(rows[0])} columns")
    print(f"    Row 1 (labels):    {len(rows[1])} columns")
    print(f"    Row 2 (import):    {len(rows[2])} columns")
    for i in range(3, len(rows)):
        if len(rows[i]) != len(rows[0]):
            print(f"    ROW {i}: COLUMN COUNT MISMATCH ({len(rows[i])} vs {len(rows[0])})")
    data_rows = len(rows) - 3
    status = "OK" if data_rows == EXPECTED_RESPONDENTS else "WARNING"
    print(f"    Data rows: {data_rows}  [{status}: expected {EXPECTED_RESPONDENTS}]")

print("\n--- 2. Pandas DataFrame shape ---")
val = pd.read_csv(VALUES_PATH, skiprows=[1, 2])
lab = pd.read_csv(LABELS_PATH, skiprows=[1, 2])
print(f"  VALUES: {val.shape[0]} rows x {val.shape[1]} columns")
print(f"  LABELS: {lab.shape[0]} rows x {lab.shape[1]} columns")

print("\n--- 3. ResponseId alignment ---")
misaligned = sum(
    1 for i in range(min(len(val), len(lab)))
    if val.iloc[i]["ResponseId"] != lab.iloc[i]["ResponseId"]
)
if misaligned == 0:
    print(f"  OK: All {min(len(val), len(lab))} ResponseIds match row-for-row.")
else:
    print(f"  ERROR: {misaligned} rows misaligned!")

print("\n--- 4. Column alignment spot-check ---")
for col, valid in [("Q1", [1, 2, 3, 4]), ("Q18", [1, 2, 3, 4])]:
    vals = val[col].dropna().unique()
    invalid = [v for v in vals if v not in valid]
    if invalid:
        print(f"  ERROR: {col} has unexpected values: {invalid}")
    else:
        print(f"  OK: {col} values = {sorted(vals)}")

print(f"  Finished values: {val['Finished'].unique()}")

print("\n--- 5. Multi-select cross-check: Q4 ---")
Q4_MAP = {
    1: "Entry-level employees", 2: "Executive assistants", 3: "Finance",
    4: "Human resources", 5: "IT helpdesk", 6: "Legal",
    7: "Marketing/PR", 8: "Other",
}
mismatches = 0
for i in range(len(val)):
    v_str = str(val.iloc[i]["Q4"])
    l_str = str(lab.iloc[i]["Q4"])
    if v_str == "nan":
        continue
    codes = [int(x.strip()) for x in v_str.split(",") if x.strip().isdigit()]
    for c in codes:
        label = Q4_MAP.get(c, "")
        if label and label != "Other" and label.lower() not in l_str.lower():
            print(f"  ROW {i}: Code {c} label '{label}' NOT in LABELS: '{l_str[:80]}'")
            mismatches += 1
if mismatches == 0:
    print(f"  OK: All Q4 codes match their labels.")

print("\n--- 6. Rank-order cross-check: Q17 GROUP columns ---")
Q17_MAP = {
    1: "Scarcity", 2: "Authority", 3: "Peer influence",
    4: "Reciprocity", 5: "Commitment", 6: "Curiosity", 7: "Fear",
}
mismatches = 0
for slot in range(5):
    col = f"Q17_{slot}_GROUP"
    for i in range(len(val)):
        v = val.iloc[i][col]
        l = lab.iloc[i][col]
        if pd.isna(v):
            continue
        codes = []
        for part in str(v).split(","):
            try:
                codes.append(int(float(part.strip())))
            except (ValueError, TypeError):
                pass
        l_str = str(l)
        for c in codes:
            label = Q17_MAP.get(c, "")
            if label and label.lower() not in l_str.lower():
                print(f"  ROW {i} SLOT {slot}: Code {c} ('{label}') NOT in label '{l_str[:60]}'")
                mismatches += 1
if mismatches == 0:
    print(f"  OK: All Q17 rank codes match their labels across all slots.")

print("\n" + "=" * 70)
print("INTEGRITY CHECK COMPLETE")
print("=" * 70)
