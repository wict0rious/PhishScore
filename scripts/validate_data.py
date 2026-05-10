"""Cross-validate the survey data interpretation.

For each question, this script pairs every value code with the corresponding
label from the LABELS CSV, compares against the config mapping, and flags
any mismatches or unmapped codes. It also recomputes Borda scores manually
for ranked questions as a sanity check on the analysis pipeline.
"""
from collections import Counter

import pandas as pd

from phishscore.config import (
    Q1_MAP, Q2_MAP, Q3_MAP, Q4_MAP, Q5_MAP, Q6_ITEMS,
    Q7_MAP, Q8_MAP, Q9_MAP, Q10_MAP, Q11_MAP, Q12_MAP,
    Q13_MAP, Q14_MAP, Q15_MAP, Q16_ITEMS, Q17_ITEMS,
    Q18_MAP, Q19_ITEMS, Q20_MAP, VALUES_CSV, LABELS_CSV,
)

val = pd.read_csv(VALUES_CSV, skiprows=[1, 2])
lab = pd.read_csv(LABELS_CSV, skiprows=[1, 2])

val = val[val["Finished"].astype(str).isin(["1", "True", "1.0"])].reset_index(drop=True)
lab = lab[lab["Finished"].astype(str).isin(["1", "True", "1.0"])].reset_index(drop=True)

errors = []
warnings = []
n = len(val)

print(f"Validating {n} responses (VALUES) against {len(lab)} (LABELS)...")
if n != len(lab):
    errors.append(f"Row count mismatch: VALUES={n}, LABELS={len(lab)}")
print("=" * 70)


def validate_single_select(q_col, config_map, q_name):
    print(f"\n--- {q_name} ({q_col}) ---")
    seen = {}
    mismatches = 0
    for i in range(n):
        v = val.iloc[i][q_col]
        l = lab.iloc[i][q_col]
        if pd.isna(v) and pd.isna(l):
            continue
        if pd.isna(v) or pd.isna(l):
            print(f"  ROW {i}: VALUE={v} but LABEL={l}")
            mismatches += 1
            continue
        v_int = int(float(v))
        if v_int not in config_map:
            msg = f"ROW {i}: Code {v_int} unmapped (label='{l}')"
            print(f"  {msg}")
            errors.append(f"{q_col}: {msg}")
            mismatches += 1
        seen[v_int] = str(l)

    for code in sorted(seen):
        actual = seen[code]
        cfg = config_map.get(code, "UNMAPPED")
        match = "OK" if cfg.lower().startswith(actual[:20].lower()) or actual.lower().startswith(cfg[:20].lower()) else "CHECK"
        print(f"    Code {code}: Config='{cfg}' | Data='{actual}' [{match}]")
        if match == "CHECK":
            warnings.append(f"{q_col}: Code {code} cfg='{cfg}' vs data='{actual}'")

    print(f"  {'PASSED' if mismatches == 0 else f'{mismatches} mismatches'}.")


def validate_multi_select(q_col, config_map, q_name):
    print(f"\n--- {q_name} ({q_col}) ---")
    all_codes_seen = set()
    counts = Counter()
    for i in range(n):
        v_str = str(val.iloc[i][q_col])
        if v_str == "nan":
            continue
        codes = [int(x.strip()) for x in v_str.split(",") if x.strip().isdigit()]
        all_codes_seen.update(codes)
        counts.update(codes)

    print(f"  Codes in data:   {sorted(all_codes_seen)}")
    print(f"  Codes in config: {sorted(config_map.keys())}")
    unmapped = all_codes_seen - set(config_map)
    if unmapped:
        msg = f"UNMAPPED codes: {unmapped}"
        print(f"  {msg}")
        errors.append(f"{q_col}: {msg}")

    print(f"  Counts (code: count/n, pct):")
    for code in sorted(config_map):
        c = counts.get(code, 0)
        print(f"    {code} ({config_map[code]}): {c}/{n} = {round(c / n * 100, 1)}%")
    print("  PASSED.")


def validate_rank_order(q_prefix, num_slots, config_map, q_name):
    print(f"\n--- {q_name} ({q_prefix}, {num_slots} slots) ---")
    all_codes_seen = set()
    scores = {item_id: 0 for item_id in config_map}
    appearances = {item_id: 0 for item_id in config_map}
    mismatches = 0

    for slot in range(num_slots):
        weight = num_slots - slot
        col = f"{q_prefix}_{slot}_GROUP"
        if col not in val.columns:
            warnings.append(f"{col} not found")
            continue
        for i in range(n):
            v = val.iloc[i][col]
            if pd.isna(v):
                continue
            codes = []
            for part in str(v).split(","):
                try:
                    codes.append(int(float(part.strip())))
                except (ValueError, TypeError):
                    pass
            all_codes_seen.update(codes)
            for c in codes:
                if c not in config_map:
                    msg = f"ROW {i} SLOT {slot}: code {c} unmapped"
                    print(f"  {msg}")
                    errors.append(f"{q_prefix}: {msg}")
                    mismatches += 1
                else:
                    scores[c] += weight
                    appearances[c] += 1

    print(f"  Codes in data:   {sorted(all_codes_seen)}")
    print(f"  Codes in config: {sorted(config_map.keys())}")
    max_possible = num_slots * n
    print(f"  Manual Borda scores:")
    for item_id in sorted(config_map):
        raw = scores[item_id]
        norm = round(raw / max_possible, 4) if max_possible else 0
        print(f"    {item_id} ({config_map[item_id]}): raw={raw}, ranked_by={appearances[item_id]}, norm={norm}")
    print(f"  {'PASSED' if mismatches == 0 else f'{mismatches} mismatches'}.")


validate_single_select("Q1", Q1_MAP, "Years of experience")
validate_multi_select("Q2", Q2_MAP, "Primary role")
validate_multi_select("Q3", Q3_MAP, "Organizations assessed")
validate_multi_select("Q4", Q4_MAP, "Most susceptible departments")
validate_multi_select("Q5", Q5_MAP, "Least susceptible departments")
validate_rank_order("Q6", 3, Q6_ITEMS, "Employee selection factors")
validate_multi_select("Q7", Q7_MAP, "Indicators of NOT engaging")
validate_single_select("Q8", Q8_MAP, "Industry norms affect craft?")

print(f"\n--- Q9 (Regional differences) ---")
q9_counts = Counter()
for i in range(n):
    v = val.iloc[i]["Q9"]
    if pd.notna(v):
        q9_counts[int(float(v))] += 1
total_q9 = sum(q9_counts.values())
for code in sorted(Q9_MAP):
    c = q9_counts.get(code, 0)
    pct = round(c / total_q9 * 100, 1) if total_q9 else 0
    print(f"  {code} ({Q9_MAP[code]}): {c}/{total_q9} = {pct}%")

validate_single_select("Q10", Q10_MAP, "Time affects success?")
validate_multi_select("Q11", Q11_MAP, "Pretext design factors")
validate_multi_select("Q12", Q12_MAP, "Best send times")
validate_multi_select("Q13", Q13_MAP, "OSINT sources")

print(f"\n--- Q14 (Tools/automation) ---")
q14_counts = Counter()
for i in range(n):
    v = val.iloc[i]["Q14"]
    if pd.notna(v):
        q14_counts[int(float(v))] += 1
total_q14 = sum(q14_counts.values())
for code in sorted(Q14_MAP):
    c = q14_counts.get(code, 0)
    pct = round(c / total_q14 * 100, 1) if total_q14 else 0
    print(f"  {code} ({Q14_MAP[code]}): {c}/{total_q14} = {pct}%")

validate_single_select("Q15", Q15_MAP, "Personalize with internal language?")
validate_rank_order("Q16", 3, Q16_ITEMS, "Persona crafting approach")
validate_rank_order("Q17", 5, Q17_ITEMS, "Psychological levers")
validate_single_select("Q18", Q18_MAP, "Emotional tone importance")
validate_rank_order("Q19", 3, Q19_ITEMS, "Pretext credibility factors")
validate_multi_select("Q20", Q20_MAP, "Success metrics tracked")

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print(f"  Total respondents: {n}")
print(f"  Errors:   {len(errors)}")
for e in errors:
    print(f"    ERROR: {e}")
print(f"  Warnings: {len(warnings)}")
for w in warnings:
    print(f"    WARN:  {w}")
if not errors and not warnings:
    print("  ALL CHECKS PASSED.")
elif not errors:
    print("  No errors. Warnings above are informational.")
