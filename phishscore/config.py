"""Survey value-to-label maps, taxonomies, and tunable model parameters."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SETTINGS_FILE = os.path.join(BASE_DIR, ".phishscore.json")

ASSESSMENT_MODES = ["default", "offensive", "defensive"]
DEFAULT_SETTINGS = {
    "model": "enhanced",
    "assessment": "default",
}

VALUES_CSV = os.path.join(DATA_DIR, "survey_values.csv")
LABELS_CSV = os.path.join(DATA_DIR, "survey_labels.csv")


Q1_MAP = {
    1: "2-3",
    2: "4-6",
    3: "7-9",
    4: "10+",
}

Q2_MAP = {
    1: "Red teamer",
    2: "Penetration tester",
    3: "Social engineer",
    4: "Threat emulation specialist",
    5: "Threat hunter",
    6: "SOC analyst",
    7: "OSINT analyst",
    8: "Other",
}

Q3_MAP = {
    1: "Education",
    2: "Financial services",
    3: "Fortune 1,000",
    4: "Government",
    5: "Healthcare",
    6: "Law firms",
    7: "NGOs",
    8: "Tech companies",
    9: "Other",
}

Q4_MAP = {
    1: "Entry-level employees",
    2: "Executive assistants",
    3: "Finance",
    4: "Human resources",
    5: "IT helpdesk",
    6: "Legal",
    7: "Marketing/PR",
    8: "Other",
}

Q5_MAP = Q4_MAP.copy()

Q6_ITEMS = {
    1: "Access level",
    2: "Visibility/exposure of information on employee",
    3: "Personality traits (e.g., over-sharer)",
    4: "Past breach involvement",
    5: "Responsiveness or email behavior",
    6: "Other",
}

# Q7 wording was corrected from the original survey. It asks for
# indicators that an employee is likely to NOT engage with a phish.
Q7_MAP = {
    1: "Security awareness training signals (e.g., email banners)",
    2: "Technical role (e.g., security engineer, SOC analyst)",
    3: "Multi-layer communication style (e.g., Slack follow-up expected)",
    4: "Suspicious or cautious tone in prior emails",
    5: "Known 'human firewall' champions",
    6: "Organizational culture of verification",
    7: "Other",
}

Q8_MAP = {
    1: "Yes, each industry requires a tailored approach",
    2: "Sometimes, minor tweaks usually suffice",
    3: "No, good pretexts are universally effective",
}

Q9_MAP = {
    1: "Yes",
    2: "No",
    3: "Unsure",
}

Q10_MAP = {
    1: "Yes",
    2: "No",
    3: "Unsure",
}

Q11_MAP = {
    1: "Brand familiarity",
    2: "Company size or hierarchy",
    3: "Emotional triggers (urgency, fear, reward)",
    4: "Job title or role",
    5: "Known habits or behaviors",
    6: "Social/professional norms",
    7: "Timing (seasonal/event-based)",
    8: "Other",
}

Q12_MAP = {
    1: "Avoiding Fridays/weekends",
    2: "Based on habits (from OSINT)",
    3: "Based on time zone of employee",
    4: "End of workday",
    5: "Near relevant holidays or deadlines",
    6: "Right after lunch",
    7: "Right before lunch",
    8: "Start of workdays",
    9: "Other",
}

Q13_MAP = {
    1: "Company websites",
    2: "Paste sites or breach data",
    3: "News and press releases",
    4: "Social media (LinkedIn, Facebook, Instagram, X/Twitter)",
    5: "GitHub/Stack Overflow",
    6: "Other",
}

Q14_MAP = {
    1: "Yes",
    2: "No",
}

Q15_MAP = {
    1: "Yes, frequently",
    2: "Occasionally",
    3: "Rarely",
    4: "No",
}

Q16_ITEMS = {
    1: "Reuse known/real internal personas",
    2: "Create realistic but fake personas",
    3: "Use external or third-party personas (e.g., vendors, recruiters)",
    4: "Keep sender vague or generic",
    5: "It depends",
}

Q17_ITEMS = {
    1: "Scarcity",
    2: "Authority",
    3: "Peer influence/herd behavior",
    4: "Reciprocity",
    5: "Commitment/consistency",
    6: "Curiosity",
    7: "Fear",
}

Q18_MAP = {
    1: "Not important",
    2: "Somewhat important",
    3: "Important",
    4: "Very important",
}

Q19_ITEMS = {
    1: "Matches the recipient's job duties",
    2: "Uses real names or departments",
    3: "Mimics internal tone or style",
    4: "Comes from a familiar sender type (e.g., HR, IT)",
    5: "Has a plausible call to action",
    6: "Avoids obvious red flags (spelling, bad formatting)",
    7: "Includes known tools/services (e.g., DocuSign, Zoom)",
    8: "Other",
}

Q20_MAP = {
    1: "Initial email opens",
    2: "Link clicks",
    3: "Replies or email responses",
    4: "Document downloads or form submissions",
    5: "Credential submissions",
    6: "Phone calls or voice responses",
    7: "Lateral movement or access gained post-phish",
    8: "We only track initial email opens or clicks",
    9: "Other",
}

INDUSTRY_TYPES = [
    "Education",
    "Financial services",
    "Fortune 1,000",
    "Government",
    "Healthcare",
    "Law firms",
    "NGOs",
    "Tech companies",
    "Other",
]

DEPARTMENT_TYPES = [
    "Entry-level employees",
    "Executive assistants",
    "Finance",
    "Human resources",
    "IT helpdesk",
    "Legal",
    "Marketing/PR",
    "Other",
]


# Enhanced model: expanded department/industry taxonomies with blend maps
# and context modifiers inferred from the survey data and qualitative coding.

ENHANCED_DEPARTMENT_TYPES = [
    "Accounting",
    "C-Suite/Executives",
    "Compliance/Audit",
    "Customer Service",
    "Cybersecurity/InfoSec",
    "Engineering/R&D",
    "Entry-level employees",
    "Executive assistants",
    "Facilities/Admin",
    "Finance",
    "Human resources",
    "IT helpdesk",
    "IT Operations",
    "Legal",
    "Marketing/PR",
    "Operations",
    "Procurement",
    "Sales",
    "Other",
]

ENHANCED_INDUSTRY_TYPES = [
    "Consulting",
    "Education",
    "Energy/Utilities",
    "Financial services",
    "Fortune 1,000",
    "Government",
    "Healthcare",
    "Hospitality",
    "Law firms",
    "Legal/Professional Services",
    "Manufacturing",
    "Media/Entertainment",
    "NGOs",
    "Nonprofit/Charity",
    "Retail",
    "Tech companies",
    "Transportation",
    "Other",
]

# Each non-surveyed department maps to a weighted blend of surveyed ones.
# Weights must sum to 1.0. Surveyed departments use their empirical scores
# directly and are intentionally absent from this map.
DEPARTMENT_BLEND_MAP = {
    "Cybersecurity/InfoSec": {
        "blend": {"IT helpdesk": 1.0},
        "extra_offset": -0.36,
        "source": "IT helpdesk base + Q7 security-role protective offset",
    },
    "IT Operations": {
        "blend": {"IT helpdesk": 1.0},
        "extra_offset": -0.10,
        "source": "IT helpdesk base + moderate technical-awareness offset",
    },
    "C-Suite/Executives": {
        "blend": {"Executive assistants": 0.80, "Finance": 0.20},
        "extra_offset": 0.15,
        "source": "Exec assistants + Finance, boosted by Q6 access/visibility",
    },
    "Sales": {
        "blend": {"Marketing/PR": 0.60, "Entry-level employees": 0.40},
        "extra_offset": 0.0,
        "source": "Marketing/PR + Entry-level blend",
    },
    "Customer Service": {
        "blend": {"Entry-level employees": 0.50, "Human resources": 0.30, "Marketing/PR": 0.20},
        "extra_offset": 0.0,
        "source": "Entry-level + HR + Marketing/PR; high interaction volume",
    },
    "Engineering/R&D": {
        "blend": {"IT helpdesk": 0.70, "Entry-level employees": 0.30},
        "extra_offset": -0.11,
        "source": "IT helpdesk + Entry-level; technical protection offset",
    },
    "Operations": {
        "blend": {"Finance": 0.40, "Entry-level employees": 0.40, "Human resources": 0.20},
        "extra_offset": 0.0,
        "source": "Finance + Entry-level + HR blend",
    },
    "Accounting": {
        "blend": {"Finance": 0.90, "Entry-level employees": 0.10},
        "extra_offset": 0.0,
        "source": "Finance-dominant blend",
    },
    "Procurement": {
        "blend": {"Finance": 0.50, "Executive assistants": 0.30, "Legal": 0.20},
        "extra_offset": 0.0,
        "source": "Finance + Exec assistants + Legal blend",
    },
    "Compliance/Audit": {
        "blend": {"Legal": 0.70, "Finance": 0.30},
        "extra_offset": 0.0,
        "source": "Legal-dominant blend with Finance",
    },
    "Facilities/Admin": {
        "blend": {"Entry-level employees": 0.60, "Executive assistants": 0.40},
        "extra_offset": 0.0,
        "source": "Entry-level + Exec assistants blend",
    },
}

INDUSTRY_BLEND_MAP = {
    "Retail": {
        "blend": {"Fortune 1,000": 0.50, "Other": 0.50},
        "source": "Fortune 1,000 + Other blend",
    },
    "Manufacturing": {
        "blend": {"Fortune 1,000": 0.60, "Other": 0.40},
        "source": "Fortune 1,000 + Other blend",
    },
    "Energy/Utilities": {
        "blend": {"Government": 0.40, "Fortune 1,000": 0.40, "Other": 0.20},
        "source": "Government + Fortune 1,000 + Other blend",
    },
    "Hospitality": {
        "blend": {"Education": 0.50, "Other": 0.50},
        "source": "Education + Other blend",
    },
    "Media/Entertainment": {
        "blend": {"Tech companies": 0.50, "Other": 0.50},
        "source": "Tech companies + Other blend",
    },
    "Legal/Professional Services": {
        "blend": {"Law firms": 0.80, "Financial services": 0.20},
        "source": "Law firms + Financial services blend",
    },
    "Nonprofit/Charity": {
        "blend": {"NGOs": 0.90, "Education": 0.10},
        "source": "NGOs-dominant blend with Education",
    },
    "Transportation": {
        "blend": {"Government": 0.30, "Fortune 1,000": 0.50, "Other": 0.20},
        "source": "Government + Fortune 1,000 + Other blend",
    },
    "Consulting": {
        "blend": {"Tech companies": 0.30, "Financial services": 0.40, "Fortune 1,000": 0.30},
        "source": "Tech companies + Financial services + Fortune 1,000 blend",
    },
}

# modifier = (survey_pct / 100) * MODIFIER_SCALING_FACTOR
MODIFIER_SCALING_FACTOR = 0.25

CONTEXT_MODIFIERS = {
    "technical": {
        "label": "Technical/Security role",
        "value": -0.15,
        "source": "Q7 protective signal scaled by MODIFIER_SCALING_FACTOR",
    },
    "new_hire": {
        "label": "New hire (< 6 months)",
        "value": 0.15,
        "source": "Open-response: employee newness flagged as targeting signal",
    },
    "customer_facing": {
        "label": "Customer-facing",
        "value": 0.10,
        "source": "Open-response: helpfulness exploitation, high interaction volume",
    },
    "leadership": {
        "label": "Leadership/Director+",
        "value": 0.10,
        "source": "Q6: access level + visibility are top targeting factors",
    },
    "administrative": {
        "label": "Administrative/Clerical",
        "value": 0.05,
        "source": "High email volume, routine processing",
    },
    "deadline": {
        "label": "Deadline/high stress",
        "value": 0.10,
        "source": "Q12: deadline-adjacent send times are top-ranked",
    },
    "remote": {
        "label": "Remote worker",
        "value": 0.08,
        "source": "Q7: multi-layer communication is protective; absence = risk",
    },
    "high_email": {
        "label": "High email volume",
        "value": 0.08,
        "source": "Q6 responsiveness; muscle-memory clicks",
    },
    "vendor_facing": {
        "label": "Vendor-facing",
        "value": 0.08,
        "source": "Open-response: vendor impersonation effectiveness",
    },
    "org_change": {
        "label": "Recent org change",
        "value": 0.10,
        "source": "Open-response: company morale and org maturity",
    },
    "overtime": {
        "label": "Overtime/after-hours",
        "value": 0.05,
        "source": "Q12: end-of-workday send times",
    },
}


# Profile-based relevance boosts re-rank global survey recommendations
# according to target archetype and active context modifiers.
# Boost values >1.0 increase relevance, <1.0 decrease it.

DEPARTMENT_ARCHETYPE = {
    "Marketing/PR": "external_facing",
    "Sales": "external_facing",
    "Customer Service": "external_facing",
    "Human resources": "internal_support",
    "Entry-level employees": "internal_support",
    "Facilities/Admin": "internal_support",
    "Finance": "finance_ops",
    "Accounting": "finance_ops",
    "Procurement": "finance_ops",
    "C-Suite/Executives": "executive",
    "Executive assistants": "executive",
    "IT helpdesk": "technical",
    "IT Operations": "technical",
    "Engineering/R&D": "technical",
    "Cybersecurity/InfoSec": "technical",
    "Legal": "compliance",
    "Compliance/Audit": "compliance",
    "Operations": "general",
    "Other": "general",
}

ARCHETYPE_BOOSTS = {
    "external_facing": {
        "targeting_factors": {
            "Visibility/exposure of information on employee": 1.4,
            "Responsiveness or email behavior": 1.3,
        },
        "psych_levers": {
            "Reciprocity": 1.4,
            "Curiosity": 1.3,
        },
        "pretext_design": {
            "Brand familiarity": 1.3,
            "Social/professional norms": 1.3,
        },
        "credibility": {
            "Mimics internal tone or style": 1.2,
        },
        "persona": {
            "Use external or third-party personas (e.g., vendors, recruiters)": 1.3,
        },
        "osint": {
            "Social media (LinkedIn, Facebook, Instagram, X/Twitter)": 1.4,
        },
        "protective": {
            "Organizational culture of verification": 1.3,
        },
        "timing": {},
    },
    "internal_support": {
        "targeting_factors": {
            "Responsiveness or email behavior": 1.3,
            "Personality traits (e.g., over-sharer)": 1.3,
        },
        "psych_levers": {
            "Authority": 1.4,
            "Peer influence/herd behavior": 1.3,
        },
        "pretext_design": {
            "Company size or hierarchy": 1.3,
            "Emotional triggers (urgency, fear, reward)": 1.3,
        },
        "credibility": {
            "Comes from a familiar sender type (e.g., HR, IT)": 1.4,
            "Matches the recipient's job duties": 1.2,
        },
        "persona": {
            "Reuse known/real internal personas": 1.3,
        },
        "osint": {
            "Company websites": 1.2,
        },
        "protective": {
            "Security awareness training signals (e.g., email banners)": 1.3,
        },
        "timing": {},
    },
    "finance_ops": {
        "targeting_factors": {
            "Access level": 1.4,
        },
        "psych_levers": {
            "Authority": 1.4,
            "Fear": 1.3,
        },
        "pretext_design": {
            "Brand familiarity": 1.4,
            "Job title or role": 1.3,
        },
        "credibility": {
            "Has a plausible call to action": 1.3,
            "Matches the recipient's job duties": 1.3,
        },
        "persona": {
            "Use external or third-party personas (e.g., vendors, recruiters)": 1.4,
        },
        "osint": {
            "Company websites": 1.3,
        },
        "protective": {
            "Organizational culture of verification": 1.3,
        },
        "timing": {
            "Near relevant holidays or deadlines": 1.3,
        },
    },
    "executive": {
        "targeting_factors": {
            "Access level": 1.5,
            "Visibility/exposure of information on employee": 1.4,
        },
        "psych_levers": {
            "Authority": 0.7,
            "Scarcity": 1.3,
            "Fear": 1.3,
        },
        "pretext_design": {
            "Company size or hierarchy": 1.3,
            "Emotional triggers (urgency, fear, reward)": 1.3,
        },
        "credibility": {
            "Uses real names or departments": 1.3,
            "Has a plausible call to action": 1.3,
        },
        "persona": {
            "Use external or third-party personas (e.g., vendors, recruiters)": 1.3,
        },
        "osint": {
            "News and press releases": 1.4,
            "Social media (LinkedIn, Facebook, Instagram, X/Twitter)": 1.3,
        },
        "protective": {
            "Multi-layer communication style (e.g., Slack follow-up expected)": 1.3,
        },
        "timing": {},
    },
    "technical": {
        "targeting_factors": {
            "Past breach involvement": 1.3,
        },
        "psych_levers": {
            "Curiosity": 1.4,
            "Scarcity": 1.3,
            "Authority": 0.7,
        },
        "pretext_design": {
            "Known habits or behaviors": 1.3,
            "Job title or role": 1.2,
        },
        "credibility": {
            "Avoids obvious red flags (spelling, bad formatting)": 1.5,
            "Matches the recipient's job duties": 1.3,
        },
        "persona": {
            "Reuse known/real internal personas": 1.2,
        },
        "osint": {
            "GitHub/Stack Overflow": 1.5,
        },
        "protective": {
            "Technical role (e.g., security engineer, SOC analyst)": 1.4,
            "Multi-layer communication style (e.g., Slack follow-up expected)": 1.3,
        },
        "timing": {
            "Based on habits (from OSINT)": 1.3,
        },
    },
    "compliance": {
        "targeting_factors": {
            "Access level": 1.2,
        },
        "psych_levers": {
            "Authority": 1.3,
            "Commitment/consistency": 1.3,
        },
        "pretext_design": {
            "Job title or role": 1.3,
            "Brand familiarity": 1.2,
        },
        "credibility": {
            "Matches the recipient's job duties": 1.4,
        },
        "persona": {
            "Use external or third-party personas (e.g., vendors, recruiters)": 1.3,
        },
        "osint": {
            "News and press releases": 1.3,
        },
        "protective": {
            "Organizational culture of verification": 1.3,
        },
        "timing": {},
    },
    "general": {
        "targeting_factors": {},
        "psych_levers": {},
        "pretext_design": {},
        "credibility": {},
        "persona": {},
        "osint": {},
        "protective": {},
        "timing": {},
    },
}

# Modifier-based boosts stack multiplicatively on top of archetype boosts
# whenever the corresponding modifier is active for the target.
MODIFIER_BOOSTS = {
    "technical": {
        "protective": {"Technical role (e.g., security engineer, SOC analyst)": 1.3},
        "psych_levers": {"Curiosity": 1.2, "Authority": 0.8},
    },
    "new_hire": {
        "psych_levers": {"Authority": 1.3, "Peer influence/herd behavior": 1.3},
        "pretext_design": {"Company size or hierarchy": 1.3},
    },
    "customer_facing": {
        "psych_levers": {"Reciprocity": 1.3},
        "targeting_factors": {"Responsiveness or email behavior": 1.3},
    },
    "leadership": {
        "targeting_factors": {"Access level": 1.3},
        "psych_levers": {"Authority": 0.7, "Fear": 1.2},
    },
    "deadline": {
        "timing": {"Near relevant holidays or deadlines": 1.4},
        "psych_levers": {"Scarcity": 1.3, "Fear": 1.2},
    },
    "remote": {
        "protective": {"Multi-layer communication style (e.g., Slack follow-up expected)": 0.7},
        "psych_levers": {"Authority": 1.2},
    },
    "vendor_facing": {
        "persona": {"Use external or third-party personas (e.g., vendors, recruiters)": 1.4},
        "osint": {"Company websites": 1.2},
    },
    "high_email": {
        "targeting_factors": {"Responsiveness or email behavior": 1.4},
        "timing": {"Start of workdays": 1.2},
    },
    "org_change": {
        "psych_levers": {"Fear": 1.3},
        "pretext_design": {"Emotional triggers (urgency, fear, reward)": 1.3},
    },
    "overtime": {
        "timing": {"End of workday": 1.4},
    },
    "administrative": {
        "targeting_factors": {"Responsiveness or email behavior": 1.2},
        "pretext_design": {"Job title or role": 1.2},
    },
}
