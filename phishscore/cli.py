"""Interactive and scriptable CLI for PhishScore.

Examples:
    phishscore
    phishscore --model enhanced --assessment offensive \\
        --name "Nick Mullen" --department "Cybersecurity/InfoSec" \\
        --company "CT Corp" --industry "Tech companies" \\
        --modifiers "technical,remote"
"""
import argparse
import json
import os
import sys
import textwrap

from phishscore.config import (
    DEPARTMENT_TYPES, INDUSTRY_TYPES, MODELS_DIR, OUTPUT_DIR,
    ENHANCED_DEPARTMENT_TYPES, ENHANCED_INDUSTRY_TYPES,
    CONTEXT_MODIFIERS, SETTINGS_FILE, DEFAULT_SETTINGS, ASSESSMENT_MODES,
)
from phishscore.model import PhishingRiskModel
from phishscore.data_loader import load_clean_data
from phishscore.report import save_reports

MODEL_PATH = os.path.join(MODELS_DIR, "phishing_risk_model.joblib")

ANSI = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "reset": "\033[0m",
    "white": "\033[97m",
    "magenta": "\033[95m",
}


def get_colored(text, color):
    return f"{ANSI.get(color, '')}{text}{ANSI['reset']}"


def level_color(level):
    return {"Critical": "red", "High": "red", "Medium": "yellow", "Low": "green"}.get(level, "white")


def print_section(title):
    print()
    print(get_colored(f"-- {title} " + "-" * (60 - len(title)), "bold"))


def print_susceptibility_bar(score, level):
    bar_len = 40
    filled = int(score / 100 * bar_len)
    bar = "#" * filled + "." * (bar_len - filled)
    color = level_color(level)
    print(f"  Susceptibility Score: {get_colored(f'{score}/100', color)}  [{get_colored(bar, color)}]")
    print(f"  Susceptibility Level: {get_colored(level, color)}")


def print_ranked_items(items, key_name, value_name, value_suffix=""):
    for i, item in enumerate(items, 1):
        name = item[key_name]
        val = item[value_name]
        if isinstance(val, float):
            val_str = f"{val:.4f}{value_suffix}" if "weight" in value_name else f"{val}{value_suffix}"
        else:
            val_str = f"{val}{value_suffix}"
        print(f"    {i}. {name} ({val_str})")


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings = dict(DEFAULT_SETTINGS)
            settings.update(saved)
            return settings
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def print_header():
    fish_top = r"""
                                /|
                               / |                                      /|
                              /  |                                     / |
                             /    \                                   /  /
                  ____---~~~~      ~~~~------______                  /  |
___________----~~~ O \                             \~~~~---____----~~   |"""
    fish_mid_pre = r"      ~~~~~~~--_____  )      "
    fish_mid_text = "PhishScore v1.0"
    fish_mid_post = r"                            |"
    fish_bot = r"""              \_--~~~ /                             ____----~~~~-----    \
               ~~~~~~----_\ \__________--------~~~~~/                 \  |
                           \ \                                         \ |
                             \|                                         \|"""
    tagline = "           A phishing susceptibility scoring engine by "
    bigman = "@wict0rious"
    separator = "=" * 78

    print(get_colored(fish_top, "cyan"))
    print(get_colored(fish_mid_pre, "cyan") + get_colored(fish_mid_text, "red") + get_colored(fish_mid_post, "cyan"))
    print(get_colored(fish_bot, "cyan"))
    print()
    print(get_colored(tagline, "cyan") + get_colored(bigman, "red"))
    print(get_colored(separator, "cyan"))


def show_main_menu(settings):
    _clear_screen()
    print_header()
    print()
    print(get_colored("  Current Settings:", "cyan"))
    _print_settings_lines(settings)
    print()
    print(f"  {get_colored('[1]', 'bold')} Run Assessment")
    print(f"  {get_colored('[2]', 'bold')} Change Settings")
    print(f"  {get_colored('[3]', 'bold')} Exit")
    print()
    return input(get_colored("  > ", "cyan")).strip()


def show_settings_menu(settings):
    model_opts = ["pure", "enhanced"]

    while True:
        _clear_screen()
        print_header()
        print()
        print(get_colored("  Settings (type a value to switch, 'back' to return):", "cyan"))
        _print_settings_lines(settings)
        print()

        choice = input(get_colored("  > ", "cyan")).strip().lower()
        if not choice:
            continue
        if choice in ("back", "b"):
            break
        if choice in model_opts:
            settings["model"] = choice
            save_settings(settings)
        elif choice in ASSESSMENT_MODES:
            settings["assessment"] = choice
            save_settings(settings)
        else:
            print(get_colored(
                f"    Unknown option. Try: {', '.join(model_opts + ASSESSMENT_MODES)}", "red"
            ))
            input(get_colored("  Press Enter to continue...", "cyan"))


def _clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _print_settings_lines(settings):
    m = settings["model"]
    a = settings["assessment"]
    model_parts = []
    for o in ["pure", "enhanced"]:
        label = o.capitalize()
        color = "green" if o == m else "red"
        prefix = "> " if o == m else "  "
        model_parts.append(get_colored(f"{prefix}{label}", color))
    mode_parts = []
    for o in ASSESSMENT_MODES:
        label = o.capitalize()
        color = "green" if o == a else "red"
        prefix = "> " if o == a else "  "
        mode_parts.append(get_colored(f"{prefix}{label}", color))
    print(f"    Model:           {' / '.join(model_parts)}")
    print(f"    Assessment Mode: {' / '.join(mode_parts)}")


def select_modifiers():
    mod_keys = list(CONTEXT_MODIFIERS.keys())
    print()
    print(get_colored("  Select applicable modifiers (comma-separated, enter to skip):", "cyan"))

    col1_count = (len(mod_keys) + 1) // 2
    for i in range(col1_count):
        left_idx = i
        right_idx = i + col1_count
        left = f"    {left_idx + 1:>2}. {CONTEXT_MODIFIERS[mod_keys[left_idx]]['label']}"
        if right_idx < len(mod_keys):
            right = f"{right_idx + 1:>2}. {CONTEXT_MODIFIERS[mod_keys[right_idx]]['label']}"
            print(f"{left:<40s}{right}")
        else:
            print(left)

    print()
    raw = input(get_colored("  > ", "cyan")).strip()
    if not raw:
        return []

    selected = []
    for part in raw.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(mod_keys):
                selected.append(mod_keys[idx])
        except ValueError:
            if part in CONTEXT_MODIFIERS:
                selected.append(part)
    return selected


def collect_assessment_inputs(settings):
    model_mode = settings["model"]
    dept_list = ENHANCED_DEPARTMENT_TYPES if model_mode == "enhanced" else DEPARTMENT_TYPES
    ind_list = ENHANCED_INDUSTRY_TYPES if model_mode == "enhanced" else INDUSTRY_TYPES

    print()
    name = input(get_colored("  Enter target name: ", "cyan")).strip() or "Unknown"

    print()
    company = input(get_colored("  Enter company name: ", "cyan")).strip() or "Unknown"

    print()
    print(get_colored("  Available industries:", "cyan"))
    for i, ind in enumerate(ind_list, 1):
        print(f"    {i:>2}. {ind}")
    print()
    ind_input = input(get_colored("  Select industry (number or name): ", "cyan")).strip()
    try:
        industry = ind_list[int(ind_input) - 1]
    except (ValueError, IndexError):
        industry = ind_input

    print()
    print(get_colored("  Available departments:", "cyan"))
    for i, dept in enumerate(dept_list, 1):
        print(f"    {i:>2}. {dept}")
    print()
    dept_input = input(get_colored("  Select department (number or name): ", "cyan")).strip()
    try:
        department = dept_list[int(dept_input) - 1]
    except (ValueError, IndexError):
        department = dept_input

    modifier_keys = select_modifiers() if model_mode == "enhanced" else []
    return name, department, company, industry, modifier_keys


def display_target_profile(result):
    target = result["target"]
    enhanced = result.get("enhanced_info")

    print_section("TARGET PROFILE")
    print(f"  Name:       {target['name']}")
    print(f"  Department: {target['department']}")
    print(f"  Company:    {target['company']}")
    print(f"  Industry:   {target['industry']}")

    if enhanced:
        if enhanced.get("department_blend_source"):
            print(get_colored(
                f"  Dept. source: inferred via [{enhanced['department_blend_source']}]",
                "yellow",
            ))
        if enhanced.get("industry_blend_source"):
            print(get_colored(
                f"  Ind. source:  inferred via [{enhanced['industry_blend_source']}]",
                "yellow",
            ))
        if enhanced.get("active_modifiers"):
            mod_strs = [
                f"{m['label']} ({m['value']:+.2f})"
                for m in enhanced["active_modifiers"]
            ]
            print(get_colored(f"  Modifiers:    {', '.join(mod_strs)}", "yellow"))


def display_susceptibility_assessment(result):
    sa = result["susceptibility_assessment"]
    print_section("SUSCEPTIBILITY ASSESSMENT")
    print_susceptibility_bar(sa["susceptibility_score"], sa["susceptibility_level"])
    print(f"  Dept. Susceptibility (raw): {sa['department_susceptibility_raw']:+.4f}")
    print(f"  Industry Modifier:          {sa['industry_modifier']:+.4f}")
    if sa.get("modifier_total", 0.0) != 0.0:
        print(f"  Context Modifiers:          {sa['modifier_total']:+.4f}")
    print(f"  Department Rank:            {sa['department_rank']}")


def display_footer():
    print()
    print(get_colored("=" * 70, "cyan"))
    print()


def display_interpretive_note(result):
    ss = result["susceptibility_assessment"]["susceptibility_score"]
    if ss > 50:
        comparison = f"more susceptible than ~{ss}%"
    else:
        comparison = f"more resistant than ~{100 - ss}%"
    print_section("NOTE")
    note = (
        f"This is a RELATIVE susceptibility score for this employee \"profile\", "
        f"and NOT a per-attempt probability. A score of {ss}/100 means this "
        f"employee profile is {comparison} of typical organizational roles. "
        f"Actual individual results will vary, as personality, experience and "
        f"situational awareness differ from person to person, and from "
        f"time to time."
    )
    wrapped = textwrap.fill(note, width=66, initial_indent="  ", subsequent_indent="  ")
    print(get_colored(wrapped, "cyan"))


def display_results_default(result):
    attack = result["attack_recommendations"]
    defense = result["defensive_insights"]
    reasoning = result["reasoning"]
    model_info = result["model_info"]
    model_mode = model_info.get("mode", "pure")

    print_section("MODEL")
    if model_mode == "enhanced":
        print(get_colored("  Mode: Enhanced (survey data + qualitative analysis)", "yellow"))
    else:
        print(get_colored("  Mode: Pure (direct survey data only)", "cyan"))

    display_target_profile(result)
    display_susceptibility_assessment(result)

    print_section("RECOMMENDED ATTACK APPROACH")

    print(get_colored("\n  Targeting Factors (why this target):", "magenta"))
    print_ranked_items(attack["targeting_factors"], "factor", "weight")

    print(get_colored("\n  Psychological Levers (how to persuade):", "magenta"))
    print_ranked_items(attack["psychological_levers"], "lever", "weight")

    print(get_colored("\n  Pretext Design (what to say):", "magenta"))
    print_ranked_items(attack["pretext_design"], "factor", "selected_by_pct", "%")

    print(get_colored("\n  Credibility Factors (how to make it believable):", "magenta"))
    print_ranked_items(attack["credibility_factors"], "factor", "weight")

    print(get_colored("\n  Optimal Timing (when to send):", "magenta"))
    print_ranked_items(attack["optimal_timing"], "timing", "selected_by_pct", "%")

    print(get_colored("\n  Persona Approach (who to impersonate):", "magenta"))
    print_ranked_items(attack["persona_approach"], "approach", "weight")

    print(get_colored("\n  OSINT Sources (where to gather intel):", "magenta"))
    print_ranked_items(attack["osint_sources"], "source", "selected_by_pct", "%")

    print_section("DEFENSIVE INSIGHTS")
    print(get_colored("  Protective Factors:", "green"))
    print_ranked_items(defense["protective_factors"], "factor", "selected_by_pct", "%")
    print()
    wrapped = textwrap.fill(defense["recommendation"], width=66, initial_indent="  ", subsequent_indent="  ")
    print(get_colored(wrapped, "green"))

    print_section("REASONING")
    wrapped = textwrap.fill(reasoning, width=66, initial_indent="  ", subsequent_indent="  ")
    print(wrapped)

    display_interpretive_note(result)
    display_footer()


def display_results_offensive(result):
    attack = result["attack_recommendations"]

    display_target_profile(result)
    display_susceptibility_assessment(result)

    print_section("ATTACK APPROACH")

    print(get_colored("\n  Targeting Factors (why this target):", "magenta"))
    print_ranked_items(attack["targeting_factors"], "factor", "weight")

    print(get_colored("\n  Psychological Levers (how to persuade):", "magenta"))
    print_ranked_items(attack["psychological_levers"], "lever", "weight")

    print(get_colored("\n  Pretext Design (what to say):", "magenta"))
    print_ranked_items(attack["pretext_design"], "factor", "selected_by_pct", "%")

    print(get_colored("\n  Credibility Factors (how to make it believable):", "magenta"))
    print_ranked_items(attack["credibility_factors"], "factor", "weight")

    print(get_colored("\n  Optimal Timing (when to send):", "magenta"))
    print_ranked_items(attack["optimal_timing"], "timing", "selected_by_pct", "%")

    print(get_colored("\n  Persona Approach (who to impersonate):", "magenta"))
    print_ranked_items(attack["persona_approach"], "approach", "weight")

    display_interpretive_note(result)
    display_footer()


def display_results_defensive(result):
    attack = result["attack_recommendations"]
    defense = result["defensive_insights"]
    reasoning = result["reasoning"]

    display_target_profile(result)
    display_susceptibility_assessment(result)

    print_section("TOP THREATS (brief)")
    top_factor = attack["targeting_factors"][0]["factor"] if attack["targeting_factors"] else "N/A"
    top_lever = attack["psychological_levers"][0]["lever"] if attack["psychological_levers"] else "N/A"
    top_pretext = attack["pretext_design"][0]["factor"] if attack["pretext_design"] else "N/A"
    top_timing = attack["optimal_timing"][0]["timing"] if attack["optimal_timing"] else "N/A"
    top_osint = attack["osint_sources"][0]["source"] if attack["osint_sources"] else "N/A"
    print(f"  Primary targeting factor:  {top_factor}")
    print(f"  Top psychological lever:   {top_lever}")
    print(f"  Leading pretext approach:  {top_pretext}")
    print(f"  Best attack timing:        {top_timing}")
    print(f"  Primary OSINT source:      {top_osint}")

    print_section("DEFENSIVE INSIGHTS")
    print(get_colored("  Protective Factors:", "green"))
    print_ranked_items(defense["protective_factors"], "factor", "selected_by_pct", "%")
    print()
    wrapped = textwrap.fill(defense["recommendation"], width=66, initial_indent="  ", subsequent_indent="  ")
    print(get_colored(wrapped, "green"))

    print_section("REASONING")
    wrapped = textwrap.fill(reasoning, width=66, initial_indent="  ", subsequent_indent="  ")
    print(wrapped)

    display_interpretive_note(result)
    display_footer()


def display_results(result, assessment_mode="default"):
    if assessment_mode == "offensive":
        display_results_offensive(result)
    elif assessment_mode == "defensive":
        display_results_defensive(result)
    else:
        display_results_default(result)


def ensure_model():
    if os.path.exists(MODEL_PATH):
        return PhishingRiskModel.load(MODEL_PATH)

    print(get_colored("  Training model from survey data...", "yellow"))
    df, _ = load_clean_data()
    model = PhishingRiskModel().fit(df)
    os.makedirs(MODELS_DIR, exist_ok=True)
    model.save(MODEL_PATH)
    print(get_colored(f"  Model trained on {len(df)} responses and saved.", "green"))
    return model


def main():
    parser = argparse.ArgumentParser(
        description="PhishScore - A phishing susceptibility scoring engine"
    )
    parser.add_argument("--name", help="Target name (label only)")
    parser.add_argument("--department", help="Target department")
    parser.add_argument("--company", help="Company name (label only)")
    parser.add_argument("--industry", help="Industry type")
    parser.add_argument(
        "--model", choices=["pure", "enhanced"], default=None,
        help="Model mode: 'pure' (survey data only) or 'enhanced' (with inferences)",
    )
    parser.add_argument(
        "--assessment", choices=ASSESSMENT_MODES, default=None,
        help="Output mode: 'default', 'offensive', or 'defensive'",
    )
    parser.add_argument(
        "--modifiers",
        help="Comma-separated modifier keys for enhanced mode "
             "(e.g. 'technical,remote,deadline')",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument(
        "--report", action="store_true",
        help="Export results as JSON, TXT and HTML to the output/ directory",
    )
    parser.add_argument("--retrain", action="store_true", help="Force retrain the model")
    args = parser.parse_args()

    if args.retrain and os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)

    model = ensure_model()
    settings = load_settings()

    if args.model:
        settings["model"] = args.model
    if args.assessment:
        settings["assessment"] = args.assessment

    is_direct = all([args.name, args.department, args.company, args.industry])

    if is_direct:
        name = args.name
        department = args.department
        company = args.company
        industry = args.industry
        modifier_keys = []
        if args.modifiers:
            modifier_keys = [k.strip() for k in args.modifiers.split(",") if k.strip()]
    else:
        while True:
            choice = show_main_menu(settings)
            if choice == "1":
                break
            elif choice == "2":
                show_settings_menu(settings)
            elif choice == "3":
                print()
                print(get_colored("  Goodbye.", "cyan"))
                print()
                sys.exit(0)

        name, department, company, industry, modifier_keys = collect_assessment_inputs(settings)

    result = model.predict(
        name, department, company, industry,
        mode=settings["model"], modifier_keys=modifier_keys,
    )

    should_report = args.report
    if not should_report and not args.json and not is_direct:
        print()
        save_choice = input(
            get_colored("  Save report? (y/N): ", "cyan")
        ).strip().lower()
        should_report = save_choice in ("y", "yes")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        display_results(result, assessment_mode=settings["assessment"])

    if should_report:
        report_dir = os.path.join(OUTPUT_DIR, "reports")
        paths = save_reports(result, report_dir, assessment_mode=settings["assessment"])
        base, _ = os.path.splitext(next(iter(paths.values())))
        exts = ",".join(paths.keys())
        print(get_colored(f"  Reports saved: {base}.{exts}", "green"))


if __name__ == "__main__":
    main()
