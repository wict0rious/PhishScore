"""Render assessment results as plain text, JSON and HTML."""
import json
import os
import textwrap
from datetime import datetime


def _susceptibility_bar_text(score, bar_len=40):
    filled = int(score / 100 * bar_len)
    return "#" * filled + "." * (bar_len - filled)


def _section(title):
    return f"-- {title} " + "-" * (60 - len(title))


def _build_header(result):
    target = result["target"]
    sa = result["susceptibility_assessment"]
    model_info = result["model_info"]
    enhanced = result.get("enhanced_info")
    mode = model_info.get("mode", "pure")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 70,
        "PhishScore - Phishing Susceptibility Assessment Report",
        f"Generated: {now}",
        "=" * 70,
        "",
        _section("MODEL"),
    ]
    if mode == "enhanced":
        lines.append("  Mode: Enhanced (survey data + qualitative analysis)")
    else:
        lines.append("  Mode: Pure (survey data only)")

    lines += [
        "",
        _section("TARGET PROFILE"),
        f"  Name:       {target['name']}",
        f"  Department: {target['department']}",
        f"  Company:    {target['company']}",
        f"  Industry:   {target['industry']}",
    ]

    if enhanced:
        if enhanced.get("department_blend_source"):
            lines.append(f"  Dept. source: inferred via [{enhanced['department_blend_source']}]")
        if enhanced.get("industry_blend_source"):
            lines.append(f"  Ind. source:  inferred via [{enhanced['industry_blend_source']}]")
        if enhanced.get("active_modifiers"):
            mod_strs = [
                f"{m['label']} ({m['value']:+.02f})"
                for m in enhanced["active_modifiers"]
            ]
            lines.append(f"  Modifiers:    {', '.join(mod_strs)}")

    bar = _susceptibility_bar_text(sa["susceptibility_score"])
    lines += [
        "",
        _section("SUSCEPTIBILITY ASSESSMENT"),
        f"  Susceptibility Score: {sa['susceptibility_score']}/100  [{bar}]",
        f"  Susceptibility Level: {sa['susceptibility_level']}",
        f"  Dept. Susceptibility (raw): {sa['department_susceptibility_raw']:+.4f}",
        f"  Industry Modifier:          {sa['industry_modifier']:+.4f}",
    ]
    if sa.get("modifier_total", 0.0) != 0.0:
        lines.append(f"  Context Modifiers:          {sa['modifier_total']:+.4f}")
    lines.append(f"  Department Rank:            {sa['department_rank']}")

    return lines


def _build_note(result):
    ss = result["susceptibility_assessment"]["susceptibility_score"]
    if ss > 50:
        comparison = f"more susceptible than ~{ss}%"
    else:
        comparison = f"more resistant than ~{100 - ss}%"
    note = (
        f"This is a RELATIVE susceptibility score for this employee \"profile\", "
        f"and NOT a per-attempt probability. A score of {ss}/100 means this "
        f"employee profile is {comparison} of typical organizational roles. "
        f"Actual individual results will vary, as personality, experience and "
        f"situational awareness differ from person to person, and from "
        f"time to time."
    )
    return [
        "",
        _section("NOTE"),
        textwrap.fill(note, width=66, initial_indent="  ", subsequent_indent="  "),
    ]


def _build_footer():
    return ["", "=" * 70]


def _build_attack_sections(result):
    attack = result["attack_recommendations"]
    lines = ["", _section("RECOMMENDED ATTACK APPROACH")]

    lines += ["", "  Targeting Factors (why this target):"]
    for i, item in enumerate(attack["targeting_factors"], 1):
        lines.append(f"    {i}. {item['factor']} ({item['weight']:.4f})")

    lines += ["", "  Psychological Levers (how to persuade):"]
    for i, item in enumerate(attack["psychological_levers"], 1):
        lines.append(f"    {i}. {item['lever']} ({item['weight']:.4f})")

    lines += ["", "  Pretext Design (what to say):"]
    for i, item in enumerate(attack["pretext_design"], 1):
        lines.append(f"    {i}. {item['factor']} ({item['selected_by_pct']}%)")

    lines += ["", "  Credibility Factors (how to make it believable):"]
    for i, item in enumerate(attack["credibility_factors"], 1):
        lines.append(f"    {i}. {item['factor']} ({item['weight']:.4f})")

    lines += ["", "  Optimal Timing (when to send):"]
    for i, item in enumerate(attack["optimal_timing"], 1):
        lines.append(f"    {i}. {item['timing']} ({item['selected_by_pct']}%)")

    lines += ["", "  Persona Approach (who to impersonate):"]
    for i, item in enumerate(attack["persona_approach"], 1):
        lines.append(f"    {i}. {item['approach']} ({item['weight']:.4f})")

    lines += ["", "  OSINT Sources (where to gather intel):"]
    for i, item in enumerate(attack["osint_sources"], 1):
        lines.append(f"    {i}. {item['source']} ({item['selected_by_pct']}%)")

    return lines


def _build_defense_sections(result):
    defense = result["defensive_insights"]
    lines = ["", _section("DEFENSIVE INSIGHTS"), "  Protective Factors:"]
    for i, item in enumerate(defense["protective_factors"], 1):
        lines.append(f"    {i}. {item['factor']} ({item['selected_by_pct']}%)")
    lines.append("")
    lines.append(textwrap.fill(defense["recommendation"], width=66,
                               initial_indent="  ", subsequent_indent="  "))
    return lines


def _build_reasoning(result):
    return [
        "",
        _section("REASONING"),
        textwrap.fill(result["reasoning"], width=66,
                      initial_indent="  ", subsequent_indent="  "),
    ]


def _build_brief_threats(result):
    attack = result["attack_recommendations"]
    top_factor = attack["targeting_factors"][0]["factor"] if attack["targeting_factors"] else "N/A"
    top_lever = attack["psychological_levers"][0]["lever"] if attack["psychological_levers"] else "N/A"
    top_pretext = attack["pretext_design"][0]["factor"] if attack["pretext_design"] else "N/A"
    top_timing = attack["optimal_timing"][0]["timing"] if attack["optimal_timing"] else "N/A"
    top_osint = attack["osint_sources"][0]["source"] if attack["osint_sources"] else "N/A"
    return [
        "",
        _section("TOP THREATS (brief)"),
        f"  Primary targeting factor:  {top_factor}",
        f"  Top psychological lever:   {top_lever}",
        f"  Leading pretext approach:  {top_pretext}",
        f"  Best attack timing:        {top_timing}",
        f"  Primary OSINT source:      {top_osint}",
    ]


def generate_text_report(result, assessment_mode="default"):
    lines = _build_header(result)

    if assessment_mode == "offensive":
        lines += _build_attack_sections(result)
        lines += _build_note(result)
    elif assessment_mode == "defensive":
        lines += _build_brief_threats(result)
        lines += _build_defense_sections(result)
        lines += _build_reasoning(result)
        lines += _build_note(result)
    else:
        lines += _build_attack_sections(result)
        lines += _build_defense_sections(result)
        lines += _build_reasoning(result)
        lines += _build_note(result)

    lines += _build_footer()
    return "\n".join(lines)


def generate_html_report(result, assessment_mode="default"):
    target = result["target"]
    text_body = generate_text_report(result, assessment_mode=assessment_mode)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PhishScore Report - {target['name']}</title>
<style>
  body {{ font-family: monospace; background: #fff; color: #222;
         max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
  pre {{ white-space: pre-wrap; word-wrap: break-word; line-height: 1.5; }}
</style>
</head>
<body>
<pre>{text_body}</pre>
</body>
</html>"""


def save_reports(result, output_dir, base_name=None, assessment_mode="default"):
    """Write the assessment as JSON, TXT and HTML, and return their paths."""
    os.makedirs(output_dir, exist_ok=True)

    if base_name is None:
        safe_name = result["target"]["name"].replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"phishscore_{safe_name}_{timestamp}"

    paths = {}

    json_path = os.path.join(output_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    paths["json"] = json_path

    txt_path = os.path.join(output_dir, f"{base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(generate_text_report(result, assessment_mode=assessment_mode))
    paths["txt"] = txt_path

    html_path = os.path.join(output_dir, f"{base_name}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(generate_html_report(result, assessment_mode=assessment_mode))
    paths["html"] = html_path

    return paths
