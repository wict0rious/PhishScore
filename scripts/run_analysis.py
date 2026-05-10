"""Run the full survey analysis and write a text report plus CSV exports
into ``output/``."""
import os

from phishscore.data_loader import load_clean_data
from phishscore.survey_analysis import run_full_analysis
from phishscore.config import OUTPUT_DIR


def export_analysis(analysis, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    lines = []

    lines += [
        "=" * 70,
        "PHISHING SURVEY ANALYSIS REPORT",
        "=" * 70,
        "",
        "-- DEMOGRAPHICS ----------------------------------------",
        "",
        "Experience Levels:",
    ]
    for _, row in analysis["demographics"]["experience"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Primary Roles:"]
    for _, row in analysis["demographics"]["roles"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Organizations Assessed:"]
    for _, row in analysis["demographics"]["organizations"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- DEPARTMENT SUSCEPTIBILITY ---------------------------",
        "",
        "Most Susceptible (Q4):",
    ]
    for _, row in analysis["susceptibility"]["most_susceptible"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Least Susceptible (Q5):"]
    for _, row in analysis["susceptibility"]["least_susceptible"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Net Department Risk Scores:"]
    for _, row in analysis["department_risk_scores"].iterrows():
        score = row["net_risk_score"]
        bar = "+" * int(max(0, score) * 20) + "-" * int(max(0, -score) * 20)
        lines.append(f"  {row['department']:30s} {score:+.4f}  [{bar}]")

    lines += [
        "",
        "-- TARGETING FACTORS (Q6, ranked) ----------------------",
        "",
    ]
    for _, row in analysis["targeting_factors"].iterrows():
        lines.append(
            f"  {row['label']:50s} score={row['raw_score']:.0f}  "
            f"ranked_by={row['times_ranked']}  norm={row['normalized_score']:.4f}"
        )

    lines += [
        "",
        "-- PROTECTIVE FACTORS (Q7) -----------------------------",
        "",
    ]
    for _, row in analysis["protective_factors"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- INDUSTRY CONTEXT (Q8, Q9) ---------------------------",
        "",
        "Industry norms affect phish crafting?",
    ]
    for _, row in analysis["industry_context"]["industry_norms"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Observed success rate differences by industry/region?"]
    for _, row in analysis["industry_context"]["regional_differences"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- TIMING (Q10, Q12) -----------------------------------",
        "",
        "Time of day/week affects success?",
    ]
    for _, row in analysis["timing"]["timing_matters"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Best send times:"]
    for _, row in analysis["timing"]["best_send_times"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- PRETEXT DESIGN FACTORS (Q11) ------------------------",
        "",
    ]
    for _, row in analysis["pretext_design"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- OSINT SOURCES (Q13) & TOOLS (Q14) -------------------",
        "",
    ]
    for _, row in analysis["osint"]["osint_sources"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")
    lines += ["", "Use tools/automation for OSINT?"]
    for _, row in analysis["osint"]["tools_automation"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- PERSONALIZATION (Q15) -------------------------------",
        "",
    ]
    for _, row in analysis["personalization"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- PERSONA CRAFTING (Q16, ranked) ----------------------",
        "",
    ]
    for _, row in analysis["persona_crafting"].iterrows():
        lines.append(
            f"  {row['label']:55s} score={row['raw_score']:.0f}  "
            f"norm={row['normalized_score']:.4f}"
        )

    lines += [
        "",
        "-- PSYCHOLOGICAL LEVERS (Q17, ranked) ------------------",
        "",
    ]
    for _, row in analysis["psych_levers"].iterrows():
        lines.append(
            f"  {row['label']:35s} score={row['raw_score']:.0f}  "
            f"norm={row['normalized_score']:.4f}"
        )

    lines += [
        "",
        "-- EMOTIONAL TONE IMPORTANCE (Q18) ---------------------",
        "",
    ]
    for _, row in analysis["emotional_tone"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += [
        "",
        "-- PRETEXT CREDIBILITY FACTORS (Q19, ranked) -----------",
        "",
    ]
    for _, row in analysis["pretext_credibility"].iterrows():
        lines.append(
            f"  {row['label']:55s} score={row['raw_score']:.0f}  "
            f"norm={row['normalized_score']:.4f}"
        )

    lines += [
        "",
        "-- SUCCESS METRICS (Q20) -------------------------------",
        "",
    ]
    for _, row in analysis["success_metrics"].iterrows():
        lines.append(f"  {row['label']}: {row['count']} ({row['pct']}%)")

    lines += ["", "=" * 70, "END OF REPORT", "=" * 70]

    report_text = "\n".join(lines)
    report_path = os.path.join(output_dir, "survey_analysis_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report saved to: {report_path}")

    dept_csv = os.path.join(output_dir, "department_risk_scores.csv")
    analysis["department_risk_scores"].to_csv(dept_csv, index=False)
    print(f"Department risk scores saved to: {dept_csv}")

    return report_text


def main():
    print("Loading and cleaning survey data...")
    df, _ = load_clean_data()
    print(f"Loaded {len(df)} valid responses.")

    print("\nRunning full analysis...")
    analysis = run_full_analysis(df)

    print("\nExporting results...")
    report = export_analysis(analysis, OUTPUT_DIR)

    try:
        print("\n" + report)
    except UnicodeEncodeError:
        print("\n" + report.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    main()
