"""Frequency, ranking, and risk score computations over the survey responses."""
import pandas as pd
from collections import Counter
from phishscore.config import (
    Q1_MAP, Q2_MAP, Q3_MAP, Q4_MAP, Q5_MAP, Q6_ITEMS,
    Q7_MAP, Q8_MAP, Q9_MAP, Q10_MAP, Q11_MAP, Q12_MAP,
    Q13_MAP, Q14_MAP, Q15_MAP, Q16_ITEMS, Q17_ITEMS,
    Q18_MAP, Q19_ITEMS, Q20_MAP,
)


def _count_multi_select(series, label_map):
    counts = Counter()
    for selections in series:
        if isinstance(selections, list):
            for val in selections:
                counts[val] += 1
    total = len(series)
    rows = []
    for code in sorted(label_map):
        c = counts.get(code, 0)
        rows.append({
            "code": code,
            "label": label_map[code],
            "count": c,
            "pct": round((c / total * 100) if total else 0, 1),
        })
    return pd.DataFrame(rows).sort_values("count", ascending=False).reset_index(drop=True)


def _count_single_select(series, label_map):
    counts = series.value_counts()
    total = series.notna().sum()
    rows = []
    for code in sorted(label_map):
        c = int(counts.get(code, 0))
        rows.append({
            "code": code,
            "label": label_map[code],
            "count": c,
            "pct": round((c / total * 100) if total else 0, 1),
        })
    return pd.DataFrame(rows).sort_values("count", ascending=False).reset_index(drop=True)


def _parse_group_codes(val):
    codes = []
    for part in str(val).split(","):
        try:
            codes.append(int(float(part.strip())))
        except (ValueError, TypeError):
            continue
    return codes


def _aggregate_rankings_from_groups(df, question_prefix, num_slots, items_map):
    """Borda aggregation of rank order responses from GROUP columns."""
    n = len(df)
    scores = {item_id: 0.0 for item_id in items_map}
    appearances = {item_id: 0 for item_id in items_map}

    for slot in range(num_slots):
        weight = num_slots - slot
        col = f"{question_prefix}_{slot}_GROUP"
        if col not in df.columns:
            continue
        for val in df[col].dropna():
            for code in _parse_group_codes(val):
                if code in items_map:
                    scores[code] += weight
                    appearances[code] += 1

    max_possible = num_slots * n
    rows = []
    for item_id in sorted(items_map):
        raw = scores[item_id]
        rows.append({
            "code": item_id,
            "label": items_map[item_id],
            "raw_score": raw,
            "times_ranked": appearances[item_id],
            "normalized_score": round((raw / max_possible) if max_possible else 0, 4),
        })
    return pd.DataFrame(rows).sort_values("raw_score", ascending=False).reset_index(drop=True)


def analyze_demographics(df):
    return {
        "experience": _count_single_select(df["Q1"], Q1_MAP),
        "roles": _count_multi_select(df["Q2"], Q2_MAP),
        "organizations": _count_multi_select(df["Q3"], Q3_MAP),
    }


def analyze_susceptibility(df):
    return {
        "most_susceptible": _count_multi_select(df["Q4"], Q4_MAP),
        "least_susceptible": _count_multi_select(df["Q5"], Q5_MAP),
    }


def analyze_targeting_factors(df):
    return _aggregate_rankings_from_groups(df, "Q6", 3, Q6_ITEMS)


def analyze_protective_factors(df):
    return _count_multi_select(df["Q7"], Q7_MAP)


def analyze_industry_norms(df):
    return {
        "industry_norms": _count_single_select(df["Q8"], Q8_MAP),
        "regional_differences": _count_single_select(df["Q9"].dropna().astype(int), Q9_MAP),
    }


def analyze_timing(df):
    return {
        "timing_matters": _count_single_select(df["Q10"], Q10_MAP),
        "best_send_times": _count_multi_select(df["Q12"], Q12_MAP),
    }


def analyze_pretext_design(df):
    return _count_multi_select(df["Q11"], Q11_MAP)


def analyze_osint_sources(df):
    return {
        "osint_sources": _count_multi_select(df["Q13"], Q13_MAP),
        "tools_automation": _count_single_select(df["Q14"].dropna().astype(int), Q14_MAP),
    }


def analyze_personalization(df):
    return _count_single_select(df["Q15"], Q15_MAP)


def analyze_persona_crafting(df):
    return _aggregate_rankings_from_groups(df, "Q16", 3, Q16_ITEMS)


def analyze_psych_levers(df):
    return _aggregate_rankings_from_groups(df, "Q17", 5, Q17_ITEMS)


def analyze_emotional_tone(df):
    return _count_single_select(df["Q18"], Q18_MAP)


def analyze_pretext_credibility(df):
    return _aggregate_rankings_from_groups(df, "Q19", 3, Q19_ITEMS)


def analyze_success_metrics(df):
    return _count_multi_select(df["Q20"], Q20_MAP)


def analyze_open_ended(df):
    """Open-response columns are stripped from the public CSV; returns
    empty lists when those columns are absent."""
    results = {}
    for col, label in [
        ("Q21", "Overlooked factors"),
        ("Q22", "Gut-feel elements"),
        ("Q23", "Suggested additional questions"),
    ]:
        if col not in df.columns:
            results[label] = []
            continue
        responses = df[col].dropna()
        responses = responses[responses.str.strip() != ""]
        results[label] = responses.tolist()
    return results


def compute_department_risk_scores(df):
    """Net department risk = (selected_most - selected_least) / n_respondents."""
    n = len(df)
    most = _count_multi_select(df["Q4"], Q4_MAP)
    least = _count_multi_select(df["Q5"], Q5_MAP)

    most_dict = dict(zip(most["code"], most["count"]))
    least_dict = dict(zip(least["code"], least["count"]))

    rows = []
    for code, label in Q4_MAP.items():
        if label == "Other":
            continue
        m = most_dict.get(code, 0)
        l = least_dict.get(code, 0)
        rows.append({
            "code": code,
            "department": label,
            "times_most_susceptible": m,
            "times_least_susceptible": l,
            "net_risk_score": round((m - l) / n, 4),
        })
    return pd.DataFrame(rows).sort_values("net_risk_score", ascending=False).reset_index(drop=True)


def compute_all_weights(df):
    return {
        "department_risk": compute_department_risk_scores(df),
        "targeting_factors": analyze_targeting_factors(df),
        "protective_factors": analyze_protective_factors(df),
        "pretext_design_factors": analyze_pretext_design(df),
        "timing": analyze_timing(df),
        "osint_sources": analyze_osint_sources(df),
        "persona_crafting": analyze_persona_crafting(df),
        "psych_levers": analyze_psych_levers(df),
        "emotional_tone": analyze_emotional_tone(df),
        "pretext_credibility": analyze_pretext_credibility(df),
        "success_metrics": analyze_success_metrics(df),
        "industry_norms": analyze_industry_norms(df),
        "personalization": analyze_personalization(df),
    }


def run_full_analysis(df):
    return {
        "demographics": analyze_demographics(df),
        "susceptibility": analyze_susceptibility(df),
        "targeting_factors": analyze_targeting_factors(df),
        "protective_factors": analyze_protective_factors(df),
        "industry_context": analyze_industry_norms(df),
        "timing": analyze_timing(df),
        "pretext_design": analyze_pretext_design(df),
        "osint": analyze_osint_sources(df),
        "personalization": analyze_personalization(df),
        "persona_crafting": analyze_persona_crafting(df),
        "psych_levers": analyze_psych_levers(df),
        "emotional_tone": analyze_emotional_tone(df),
        "pretext_credibility": analyze_pretext_credibility(df),
        "success_metrics": analyze_success_metrics(df),
        "open_ended": analyze_open_ended(df),
        "department_risk_scores": compute_department_risk_scores(df),
    }
