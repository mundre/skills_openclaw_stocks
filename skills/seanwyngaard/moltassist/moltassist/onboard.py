"""MoltAssist onboarding conversation flow.

Generates the 5-step onboarding conversation script and processes responses.
Does NOT handle channel messaging -- OpenClaw does that.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

_ROLE_PROFILES_PATH = Path(__file__).resolve().parent / "data" / "role_profiles.json"
_RESEARCH_DIR = Path(__file__).resolve().parent / "research"

# Keyword → research file mapping for loading relevant research into LLM prompts
_RESEARCH_KEYWORD_MAP: list[tuple[list[str], list[str]]] = [
    (["tech", "dev", "pm", "product", "community", "qa"],
     ["tech_roles.md", "business_roles.md"]),
    (["finance", "accounting", "bookkeeping"],
     ["finance_manufacturing_travel_roles.md"]),
    (["health", "medical", "nurse", "doctor"],
     ["healthcare_support_roles.md"]),
    (["education", "teacher", "tutor"],
     ["education_roles.md"]),
    (["travel", "logistics"],
     ["finance_manufacturing_travel_roles.md"]),
    (["creative", "design", "media"],
     ["creative_media_roles.md"]),
    (["retail", "hospitality"],
     ["retail_hospitality_roles.md"]),
    (["fitness", "wellness", "beauty"],
     ["fitness_beauty_wellness_roles.md"]),
    (["freelance", "contractor", "consultant"],
     ["professional_services_roles.md"]),
    (["gaming", "gamer", "f1", "sport", "hobby"],
     ["personal_life_deep.md", "personal_life.md"]),
]

# Professional role IDs (vs personal/hobby)
_PROFESSIONAL_ROLES = {
    "freelancer", "startup_founder", "restaurant_manager", "bar_manager",
    "general_contractor", "primary_teacher", "secondary_teacher",
    "personal_trainer", "hairdresser_barber", "beauty_therapist",
    "retail_manager", "hotel_manager", "event_planner", "wedding_planner",
    "accountant_bookkeeper", "property_manager", "recruiter",
    "marketing_manager", "sales_rep", "consultant", "lawyer",
    "doctor_gp", "nurse", "dentist", "pharmacist", "veterinarian",
    "real_estate_agent", "photographer", "videographer", "musician",
    "dj", "florist", "baker", "chef", "food_truck_operator",
    "market_stallholder", "caterer", "mobile_mechanic", "plumber",
    "electrician", "painter_decorator", "landscaper", "cleaner",
    "driving_instructor", "taxi_driver", "courier",
}


def _load_relevant_research(role_text: str, detected_role: str) -> str:
    """Load the most relevant 2-3 research files based on role keywords.

    Returns concatenated content trimmed to max 8000 chars.
    """
    text_lower = role_text.lower() + " " + detected_role.lower()
    matched_files: list[str] = []

    for keywords, files in _RESEARCH_KEYWORD_MAP:
        if any(kw in text_lower for kw in keywords):
            for f in files:
                if f not in matched_files:
                    matched_files.append(f)

    # Always include the appropriate integrations file
    if detected_role in _PROFESSIONAL_ROLES:
        integ = "integrations_professional.md"
    else:
        integ = "integrations_personal.md"
    if integ not in matched_files:
        matched_files.append(integ)

    # Cap at 3 most relevant files
    matched_files = matched_files[:3]

    chunks: list[str] = []
    total = 0
    for fname in matched_files:
        fpath = _RESEARCH_DIR / fname
        if not fpath.is_file():
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
        except OSError:
            continue
        remaining = 8000 - total
        if remaining <= 0:
            break
        if len(content) > remaining:
            content = content[:remaining]
        chunks.append(f"--- {fname} ---\n{content}")
        total += len(content)

    return "\n\n".join(chunks)

# All available notification categories
ALL_CATEGORIES = [
    "email", "calendar", "health", "finance",
    "travel", "dev", "weather", "compliance", "staff", "social",
]

# Category labels + emoji for display
CATEGORY_DISPLAY = {
    "email": "Email",
    "calendar": "Calendar",
    "health": "Health",
    "finance": "Work/Deals",
    "travel": "Travel",
    "dev": "Dev/Code",
    "weather": "Weather",
    "compliance": "Compliance",
    "staff": "Staff",
    "social": "Social",
}

# Skill requirements per category
SKILL_MAP = {
    "email": "gog",
    "calendar": "gog",
    "weather": "weather",
    "health": "healthcheck",
    "dev": "github",
    "finance": None,      # partial built-in
    "compliance": None,   # built-in
    "travel": "tripit",
    "staff": None,        # built-in
    "social": None,       # built-in
}

# Mode A fallback buttons for step 2
MODE_A_ROLE_BUTTONS = [
    "Freelancer", "Founder", "Employee", "Trades", "Teacher", "Other",
]

# Step 3 matter buttons
MATTER_BUTTONS = [
    "Email", "Calendar", "Health",
    "Work/Deals", "Travel", "Dev/Code", "Weather", "Custom",
]

# Map matter button labels back to category ids
_MATTER_TO_CATEGORY = {
    "Email": "email",
    "Calendar": "calendar",
    "Health": "health",
    "Work/Deals": "finance",
    "Travel": "travel",
    "Dev/Code": "dev",
    "Weather": "weather",
    "Custom": "custom",
}

# Map Mode A button labels to role ids
_MODE_A_BUTTON_TO_ROLE = {
    "Freelancer": "freelancer",
    "Founder": "startup_founder",
    "Employee": "general_personal",
    "Trades": "general_contractor",
    "Teacher": "primary_teacher",
    "Other": "fallback",
}


def _load_profiles() -> list[dict]:
    """Load role profiles from JSON."""
    with open(_ROLE_PROFILES_PATH) as f:
        return json.load(f)["roles"]


def detect_role(text: str) -> str:
    """Detect role from free text. Uses LLM if available, falls back to keyword matching.

    Returns role id (e.g. 'restaurant_manager') or 'fallback'.
    """
    # Try LLM first — far better at understanding context, negation, and nuance
    if _check_agent_available():
        profiles = _load_profiles()
        role_ids = [p["id"] for p in profiles if p["id"] != "fallback"]
        role_labels = {p["id"]: p["label"] for p in profiles}
        labels_list = "\n".join(f'  {rid}: {role_labels[rid]}' for rid in role_ids)

        prompt = (
            "You are classifying a user's job/life role for a notification assistant.\n\n"
            f"The user described themselves as:\n  \"{text}\"\n\n"
            "Pick the single best matching role ID from this list:\n"
            f"{labels_list}\n\n"
            "Rules:\n"
            "- Reply with ONLY the role ID — nothing else, no explanation, no punctuation\n"
            "- Honour negations: if they say 'I'm not a developer', never pick developer roles\n"
            "- Pick the most specific match, not a generic one\n"
            "- If nothing fits well, reply: fallback"
        )
        try:
            result = subprocess.run(
                ["openclaw", "agent", "--session-id", "moltassist-onboard", "-m", prompt],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                role_id = result.stdout.strip().lower().replace('"', '').replace("'", "").split()[0]
                # Validate it's a known role
                known = {p["id"] for p in profiles}
                if role_id in known:
                    return role_id
        except Exception:
            pass

    # Fallback: keyword matching with negation handling
    text_lower = text.lower()

    # Build negation blocklist — words after "not a", "i'm not", "not the", "don't", "no longer"
    import re
    negated_terms = set()
    negation_patterns = [
        r"(?:i'?m not a?n?\s*)(\w+(?:\s+\w+){0,3})",
        r"(?:not a?n?\s+)(\w+(?:\s+\w+){0,2})",
        r"(?:never been a?n?\s*)(\w+(?:\s+\w+){0,2})",
        r"(?:no longer a?n?\s*)(\w+(?:\s+\w+){0,2})",
    ]
    for pattern in negation_patterns:
        for match in re.finditer(pattern, text_lower):
            negated_terms.add(match.group(1).strip())

    profiles = _load_profiles()
    best_match = "fallback"
    best_score = 0

    for profile in profiles:
        if profile["id"] == "fallback":
            continue

        score = 0
        label = profile["label"].lower()

        # Skip if this role's label is negated
        if any(neg in label or label in neg for neg in negated_terms):
            continue

        # Check aliases
        for alias in profile.get("aliases", []):
            alias_lower = alias.lower()
            if any(neg in alias_lower for neg in negated_terms):
                continue
            if alias_lower in text_lower:
                score += 3

        # Check label
        if label in text_lower and not any(neg in label for neg in negated_terms):
            score += 3

        # Check keywords
        for keyword in profile.get("keywords", []):
            kw = keyword.lower()
            if any(neg in kw for neg in negated_terms):
                continue
            if kw in text_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_match = profile["id"]

    return best_match


def _get_profile(role_id: str) -> dict:
    """Get a single role profile by id."""
    profiles = _load_profiles()
    for p in profiles:
        if p["id"] == role_id:
            return p
    # Return fallback
    for p in profiles:
        if p["id"] == "fallback":
            return p
    return {}


def detect_installed_skills() -> list[str]:
    """Detect installed OpenClaw skills by checking known directories.

    Checks ~/.openclaw/workspace/skills/<name>/ and
    ~/.npm-global/lib/node_modules/openclaw/skills/<name>/ as reliable fallbacks.
    Also tries `clawhub list` if available.
    """
    installed = set()
    home = Path.home()

    # Check workspace skills
    ws_skills = home / ".openclaw" / "workspace" / "skills"
    if ws_skills.is_dir():
        for d in ws_skills.iterdir():
            if d.is_dir():
                installed.add(d.name)

    # Check npm-global skills
    npm_skills = home / ".npm-global" / "lib" / "node_modules" / "openclaw" / "skills"
    if npm_skills.is_dir():
        for d in npm_skills.iterdir():
            if d.is_dir():
                installed.add(d.name)

    # Try clawhub as bonus (may not be installed)
    try:
        result = subprocess.run(
            ["clawhub", "list"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                name = line.strip().split()[0] if line.strip() else ""
                if name:
                    installed.add(name)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return sorted(installed)


# Map categories to the skill they require (None = built-in)
_CATEGORY_SKILL_MAP = {
    "email": "gog",
    "calendar": "gog",
    "weather": "weather",
    "health": "healthcheck",
    "dev": "github",  # default; overridden dynamically by user's ticket_tool answer
    "finance": None,
    "compliance": None,
    "travel": "tripit",
    "staff": None,
    "social": "discord",  # default; overridden dynamically by user's community_platform answer
    "system": None,
    "custom": None,
}

# Maps user's tool answer to the clawhub skill slug for that tool
_TOOL_SKILL_MAP = {
    # Issue tracking
    "linear": "linear",
    "jira": "jira",
    "github issues": "github",
    "github": "github",
    "gitlab": "gitlab",
    "asana": "asana",
    "clickup": "clickup",
    # Note-taking / PM
    "notion": "notion",
    "obsidian": "obsidian",
    "trello": "trello",
    "apple notes": "apple-notes",
    "apple reminders": "apple-reminders",
    # Community
    "discord": "discord",
    "slack": "slack",
    "circle": None,
    # Calendar
    "google calendar": "gog",
    "outlook": "gog",
    "apple calendar": "gog",
    "calendly": None,
    # Email
    "gmail": "gog",
    "apple mail": "gog",
    # Finance
    "xero": None,
    "quickbooks": None,
    "wave": None,
    "freshbooks": None,
    # CRM
    "hubspot": None,
    "salesforce": None,
    "pipedrive": None,
    # Social
    "x (twitter)": None,
    "twitter": None,
    "instagram": None,
    "linkedin": None,
    "tiktok": None,
    # Gaming
    "pc / steam": None,
    "steam": None,
    "xbox": None,
    "playstation": None,
    "ps5": None,
    "nintendo switch": None,
    # Travel
    "tripit": "tripit",
    "google trips": "gog",
    # Health
    "apple health": "healthcheck",
    "strava": None,
    "garmin connect": None,
    "fitbit": None,
    "myfitnesspal": None,
    # Music
    "spotify": "spotify-player",
    "apple music": None,
    # Crypto
    "luno": None,
    "binance": None,
    "kraken": None,
    "coinbase": None,
    "coingecko": None,
    # Smart home
    "philips hue": "openhue",
    "google home": None,
    "amazon alexa": None,
    "apple homekit": None,
}


def _fuzzy_match_tool_to_skill(text: str) -> str | None:
    """Try to match a freeform tool name to a clawhub skill slug.

    Used when user selects 'Other' and types a custom tool name.
    Returns skill slug or None if no match / skill needs to be built.
    """
    t = text.lower().strip()
    # Direct match
    if t in _TOOL_SKILL_MAP:
        return _TOOL_SKILL_MAP[t]
    # Partial match
    for key, slug in _TOOL_SKILL_MAP.items():
        if key in t or t in key:
            return slug
    # Common aliases
    aliases = {
        "gh": "github", "gh issues": "github", "git": "github",
        "g calendar": "gog", "gcal": "gog", "google": "gog",
        "ms outlook": "gog", "office 365": "gog", "microsoft": "gog",
        "ps": None, "ps5 pro": None, "series x": None,
        "notioin": "notion",  # common typo
    }
    for alias, slug in aliases.items():
        if alias in t:
            return slug
    # No match -- mark as build needed
    return "__build_needed__"

# Templates for generating suggestions from key_triggers when no LLM is available.
# Each trigger maps to a suggestion template with placeholders.
_TRIGGER_TEMPLATES = {
    # Compliance / safety
    "liquor_licence_renewal": {
        "title": "Liquor licence renewal reminder",
        "description": "Get notified 60 days before your liquor licence expires.",
        "category": "compliance", "priority": "high",
    },
    "food_hygiene_cert_expiry": {
        "title": "Food hygiene certificate expiry",
        "description": "Alert when food safety certificates are approaching renewal.",
        "category": "compliance", "priority": "high",
    },
    "gas_certificate_expiry": {
        "title": "Gas certificate expiry warning",
        "description": "Reminder before your gas safety certificate expires.",
        "category": "compliance", "priority": "high",
    },
    "fire_safety_cert_expiry": {
        "title": "Fire safety certificate renewal",
        "description": "Don't miss your fire safety cert renewal date.",
        "category": "compliance", "priority": "high",
    },
    "food_safety_cert_expiry": {
        "title": "Food safety certificate expiry",
        "description": "Alert before HACCP or food safety certs need renewing.",
        "category": "compliance", "priority": "high",
    },
    "rsa_expiry_per_staff": {
        "title": "RSA certificate tracking per staff",
        "description": "Track which staff members have RSA certs expiring soon.",
        "category": "compliance", "priority": "high",
    },
    "music_licence_renewal": {
        "title": "Music licence renewal",
        "description": "Reminder before your music/PPL licence needs renewing.",
        "category": "compliance", "priority": "medium",
    },
    "mot_due": {
        "title": "Vehicle MOT due",
        "description": "Reminder when your vehicle MOT is coming up.",
        "category": "compliance", "priority": "high",
    },
    "builders_licence_renewal": {
        "title": "Builder's licence renewal",
        "description": "Alert before your contractor licence needs renewing.",
        "category": "compliance", "priority": "high",
    },
    "contract_works_insurance_expiry": {
        "title": "Contract works insurance expiry",
        "description": "Don't let your insurance lapse -- get reminded before expiry.",
        "category": "compliance", "priority": "high",
    },
    "inspection_booking_due": {
        "title": "Inspection booking due",
        "description": "Reminder to book required inspections before deadlines.",
        "category": "compliance", "priority": "high",
    },
    "allergen_documentation_update": {
        "title": "Allergen documentation update",
        "description": "Keep allergen records current with periodic reminders.",
        "category": "compliance", "priority": "medium",
    },
    "dietary_confirmation_overdue": {
        "title": "Dietary confirmation overdue",
        "description": "Chase up outstanding dietary requirement confirmations.",
        "category": "compliance", "priority": "high",
    },
    "pitch_permit_confirmation": {
        "title": "Pitch permit confirmation",
        "description": "Confirm your trading pitch permit is secured.",
        "category": "compliance", "priority": "medium",
    },
    # Staff
    "staff_no_show": {
        "title": "Staff no-show alert",
        "description": "Immediate alert when a staff member doesn't show up.",
        "category": "staff", "priority": "high",
    },
    "staff_no_show_day_of": {
        "title": "Staff no-show -- day of event",
        "description": "Critical alert for same-day staff no-shows.",
        "category": "staff", "priority": "high",
    },
    "staff_cert_renewal": {
        "title": "Staff certification renewal",
        "description": "Track when staff certifications need renewing.",
        "category": "staff", "priority": "medium",
    },
    # Finance
    "cover_vs_stock_mismatch": {
        "title": "Covers vs stock mismatch",
        "description": "Alert when booked covers don't match available stock levels.",
        "category": "finance", "priority": "high",
    },
    "pour_cost_variance_spike": {
        "title": "Pour cost variance spike",
        "description": "Flag when pour costs deviate significantly from expected.",
        "category": "finance", "priority": "medium",
    },
    "invoice_overdue": {
        "title": "Overdue invoice alert",
        "description": "Get notified when client invoices go past due date.",
        "category": "finance", "priority": "high",
    },
    "payment_claim_deadline": {
        "title": "Payment claim deadline",
        "description": "Reminder before progress payment claim deadlines.",
        "category": "finance", "priority": "high",
    },
    "tax_deadline": {
        "title": "Tax filing deadline",
        "description": "Don't miss your tax submission deadlines.",
        "category": "finance", "priority": "high",
    },
    "proposal_win_loss": {
        "title": "Proposal outcome notification",
        "description": "Get notified when proposals are accepted or rejected.",
        "category": "finance", "priority": "medium",
    },
    "supplier_delivery_failure": {
        "title": "Supplier delivery failure",
        "description": "Alert when a supplier delivery fails or is late.",
        "category": "finance", "priority": "high",
    },
    "loyalty_platform_billing": {
        "title": "Loyalty platform billing",
        "description": "Track billing from loyalty and rewards platforms.",
        "category": "finance", "priority": "low",
    },
    "delivery_shortage_vs_covers": {
        "title": "Delivery shortage vs bookings",
        "description": "Flag when deliveries fall short of tonight's covers.",
        "category": "finance", "priority": "high",
    },
    "waste_cost_spike": {
        "title": "Food waste cost spike",
        "description": "Alert when food waste costs jump unexpectedly.",
        "category": "finance", "priority": "medium",
    },
    "occupancy_vs_adr": {
        "title": "Occupancy vs ADR tracking",
        "description": "Monitor occupancy rates against average daily rate.",
        "category": "finance", "priority": "medium",
    },
    "equipment_hire_not_booked": {
        "title": "Equipment hire not yet booked",
        "description": "Reminder when event equipment hasn't been booked yet.",
        "category": "finance", "priority": "medium",
    },
    "sold_out_alert": {
        "title": "Sold out alert",
        "description": "Know immediately when you've sold out.",
        "category": "finance", "priority": "medium",
    },
    "milk_order_cutoff": {
        "title": "Milk order cutoff reminder",
        "description": "Don't miss the daily milk order deadline.",
        "category": "finance", "priority": "medium",
    },
    "espresso_machine_service_overdue": {
        "title": "Espresso machine service overdue",
        "description": "Alert when your machine is past its service interval.",
        "category": "finance", "priority": "medium",
    },
    # Social
    "negative_review": {
        "title": "Negative review alert",
        "description": "Get notified immediately when a negative review is posted.",
        "category": "social", "priority": "high",
    },
    "negative_review_safety": {
        "title": "Negative review -- safety concern",
        "description": "Urgent alert for reviews mentioning safety issues.",
        "category": "social", "priority": "high",
    },
    "google_review_posted": {
        "title": "New Google review",
        "description": "Notification when a new Google review is posted.",
        "category": "social", "priority": "medium",
    },
    "ota_review_score_drop": {
        "title": "OTA review score drop",
        "description": "Alert when your OTA review score drops below threshold.",
        "category": "social", "priority": "high",
    },
    # Calendar
    "allergen_flag_tonight": {
        "title": "Allergen flag for tonight's bookings",
        "description": "Pre-shift alert for allergen requirements in tonight's covers.",
        "category": "calendar", "priority": "high",
    },
    "event_prep_deadline": {
        "title": "Event prep deadline",
        "description": "Countdown to upcoming event preparation deadlines.",
        "category": "calendar", "priority": "medium",
    },
    "room_issue_vs_incoming_vip": {
        "title": "Room issue vs incoming VIP",
        "description": "Alert when rooms with issues have VIP guests arriving.",
        "category": "calendar", "priority": "high",
    },
    "long_lead_item_order_deadline": {
        "title": "Long-lead item order deadline",
        "description": "Reminder to order long-lead items before the cutoff.",
        "category": "calendar", "priority": "medium",
    },
    "subcontractor_confirmation": {
        "title": "Subcontractor confirmation",
        "description": "Chase up subcontractors who haven't confirmed attendance.",
        "category": "calendar", "priority": "medium",
    },
    "contract_renewal": {
        "title": "Contract renewal reminder",
        "description": "Heads up before client contracts come up for renewal.",
        "category": "calendar", "priority": "medium",
    },
    "client_silent_x_days": {
        "title": "Client gone quiet",
        "description": "Flag when a client hasn't responded in X days.",
        "category": "email", "priority": "medium",
    },
    # Weather
    "weather_forecast_outdoor_pitch": {
        "title": "Weather forecast for outdoor trading",
        "description": "Morning weather check for outdoor pitch decisions.",
        "category": "weather", "priority": "high",
    },
    # Dev
    "ci_cd_failure": {
        "title": "CI/CD pipeline failure",
        "description": "Immediate alert when your build or deploy pipeline fails.",
        "category": "dev", "priority": "high",
    },
    "pr_review_requested": {
        "title": "PR review requested",
        "description": "Notification when someone requests your code review.",
        "category": "dev", "priority": "medium",
    },
    "issue_assigned": {
        "title": "Issue assigned to you",
        "description": "Alert when a new issue is assigned to you.",
        "category": "dev", "priority": "medium",
    },
    "deploy_success": {
        "title": "Deployment succeeded",
        "description": "Confirmation when a deployment completes successfully.",
        "category": "dev", "priority": "low",
    },
    "security_vulnerability": {
        "title": "Security vulnerability detected",
        "description": "High-priority alert for new security vulnerabilities.",
        "category": "dev", "priority": "high",
    },
    # Email
    "vip_email": {
        "title": "VIP email received",
        "description": "Immediate notification for emails from important contacts.",
        "category": "email", "priority": "high",
    },
    "email_digest": {
        "title": "Morning email digest",
        "description": "Summary of overnight emails in your morning briefing.",
        "category": "email", "priority": "low",
    },
    # Health
    "medication_reminder": {
        "title": "Medication reminder",
        "description": "Timed reminders for medication schedules.",
        "category": "health", "priority": "high",
    },
    "health_metric_alert": {
        "title": "Health metric out of range",
        "description": "Alert when a tracked health metric exceeds your threshold.",
        "category": "health", "priority": "high",
    },
}

# Extra generic suggestions per category (used to pad out to 20-30)
_CATEGORY_EXTRAS = {
    "email": [
        {"title": "Urgent email flagged", "description": "Notify when an email is marked urgent by the sender.", "priority": "high"},
        {"title": "Email from unknown sender", "description": "Flag emails from contacts not in your address book.", "priority": "low"},
    ],
    "calendar": [
        {"title": "Meeting in 15 minutes", "description": "Reminder 15 minutes before each calendar event.", "priority": "medium"},
        {"title": "Double-booked slot", "description": "Alert when two events overlap on your calendar.", "priority": "high"},
        {"title": "Tomorrow's schedule summary", "description": "Evening preview of tomorrow's calendar.", "priority": "low"},
    ],
    "finance": [
        {"title": "Expense over threshold", "description": "Flag any expense exceeding your set threshold.", "priority": "medium"},
        {"title": "Weekly revenue summary", "description": "End-of-week revenue snapshot.", "priority": "low"},
    ],
    "weather": [
        {"title": "Severe weather warning", "description": "Alert for severe weather in your area.", "priority": "high"},
        {"title": "Rain forecast today", "description": "Morning heads-up if rain is expected.", "priority": "low"},
    ],
    "health": [
        {"title": "Daily step goal check", "description": "Evening check on whether you hit your step goal.", "priority": "low"},
        {"title": "Weekly health summary", "description": "End-of-week health metrics overview.", "priority": "low"},
    ],
    "dev": [
        {"title": "Dependency update available", "description": "Weekly digest of available package updates.", "priority": "low"},
    ],
    "social": [
        {"title": "Mention or tag alert", "description": "Know when your brand is mentioned online.", "priority": "medium"},
    ],
    "compliance": [
        {"title": "Document expiry tracker", "description": "Centralised tracking for all document expiry dates.", "priority": "medium"},
    ],
    "staff": [
        {"title": "Timesheet not submitted", "description": "Reminder when staff timesheets are overdue.", "priority": "medium"},
    ],
}


def generate_follow_up_questions(role_text: str, detected_role: str) -> list[dict]:
    """Return follow-up question dicts based on keyword matching in role_text.

    No cap on number of questions -- every meaningful signal in the role text
    gets its own question. All questions support "Other" with freeform text fallback.
    No LLM needed -- pure keyword matching.
    """
    text = role_text.lower()
    questions = []
    seen_ids: set = set()

    def add(q: dict) -> None:
        if q["id"] not in seen_ids:
            seen_ids.add(q["id"])
            questions.append(q)

    # Issue tracking / QA / tickets
    if any(k in text for k in ["linear", "jira", "ticket", "bug", "qa", "tester", "issue track",
                                 "kanban", "sprint", "backlog", "agile", "scrum"]):
        add({
            "id": "ticket_tool",
            "question": "What tool do you use for issue tracking and QA?",
            "type": "choice",
            "options": ["Linear", "Jira", "GitHub Issues", "Notion", "Trello", "Asana", "ClickUp", "Other"],
        })

    # Community platform
    if any(k in text for k in ["community", "discord", "slack", "moderat", "community manager",
                                 "forum", "members", "circle", "facebook group"]):
        add({
            "id": "community_platform",
            "question": "What platform is your community on?",
            "type": "choice",
            "options": ["Discord", "Slack", "Circle", "Facebook Group", "Reddit", "Discourse", "Other"],
        })

    # Client / freelance project tracking
    if any(k in text for k in ["freelance", "client", "invoice", "contract", "agency",
                                 "consulting", "retainer"]):
        add({
            "id": "client_tool",
            "question": "How do you track client projects and deadlines?",
            "type": "choice",
            "options": ["Notion", "Trello", "Asana", "ClickUp", "Spreadsheet", "HubSpot", "Other"],
        })

    # Code repositories
    if any(k in text for k in ["github", "gitlab", "bitbucket", "code repo", "repository",
                                 "openclaw", "claude code", "codex", "dev project", "coding",
                                 "software", "developer", "engineer", "rebuild", "build"]):
        add({
            "id": "repo_tool",
            "question": "What do you use for code repositories?",
            "type": "choice",
            "options": ["GitHub", "GitLab", "Bitbucket", "Other"],
        })

    # Personal project management
    if any(k in text for k in ["personal project", "side project", "hobby project", "personal dev",
                                 "build for myself", "build myself", "own project", "project idea",
                                 "personal app", "never launch", "hardly launch"]):
        add({
            "id": "personal_project_tool",
            "question": "How do you track your personal projects and ideas?",
            "type": "choice",
            "options": ["Notion", "Obsidian", "Trello", "GitHub Projects", "Apple Notes", "Spreadsheet", "Other"],
        })

    # Calendar / scheduling tool
    if any(k in text for k in ["calendar", "meeting", "standup", "schedule", "appointment",
                                 "google calendar", "outlook", "teams"]):
        add({
            "id": "calendar_tool",
            "question": "What calendar or scheduling tool do you use?",
            "type": "choice",
            "options": ["Google Calendar", "Outlook", "Apple Calendar", "Calendly", "Other"],
        })

    # Email client
    if any(k in text for k in ["email", "gmail", "outlook", "inbox", "mail"]):
        add({
            "id": "email_client",
            "question": "What email client do you use?",
            "type": "choice",
            "options": ["Gmail", "Outlook", "Apple Mail", "Other"],
        })

    # Finance / invoicing
    if any(k in text for k in ["invoice", "billing", "accounting", "xero", "quickbooks",
                                 "wave", "freshbooks", "payroll", "expense"]):
        add({
            "id": "finance_tool",
            "question": "What tool do you use for invoicing or accounting?",
            "type": "choice",
            "options": ["Xero", "QuickBooks", "Wave", "FreshBooks", "Spreadsheet", "Other"],
        })

    # CRM / sales
    if any(k in text for k in ["crm", "hubspot", "salesforce", "pipedrive", "sales",
                                 "lead", "prospect", "customer"]):
        add({
            "id": "crm_tool",
            "question": "What CRM or sales tool do you use?",
            "type": "choice",
            "options": ["HubSpot", "Salesforce", "Pipedrive", "Notion", "Spreadsheet", "Other"],
        })

    # Social media
    if any(k in text for k in ["twitter", "x.com", "instagram", "linkedin", "tiktok",
                                 "social media", "posting", "content creator", "influencer"]):
        add({
            "id": "social_platform", "multi": True,
            "question": "Which social media platforms do you actively manage?",
            "type": "choice",
            "options": ["X (Twitter)", "Instagram", "LinkedIn", "TikTok", "Facebook", "Other"],
        })

    # Gaming / entertainment
    if any(k in text for k in ["game", "gamer", "gaming", "xbox", "playstation", "ps5", "ps4",
                                 "nintendo", "steam", "pc gaming", "esport"]):
        add({
            "id": "gaming_platform", "multi": True,
            "question": "Which gaming platforms do you play on?",
            "type": "choice",
            "options": ["PC / Steam", "Xbox", "PlayStation", "Nintendo Switch", "Mobile", "Other"],
        })

    # Travel
    if any(k in text for k in ["travel", "trip", "fly", "flight", "passport", "hotel",
                                 "airbnb", "booking", "visa"]):
        add({
            "id": "travel_tool",
            "question": "How do you manage your travel plans?",
            "type": "choice",
            "options": ["Google Trips", "TripIt", "Notion", "Spreadsheet", "Nothing yet", "Other"],
        })

    # Health / fitness
    if any(k in text for k in ["gym", "fitness", "workout", "run", "exercise", "health",
                                 "apple health", "strava", "garmin", "fitbit"]):
        add({
            "id": "health_tool",
            "question": "What do you use to track health or fitness?",
            "type": "choice",
            "options": ["Apple Health", "Strava", "Garmin Connect", "Fitbit", "MyFitnessPal", "Other"],
        })

    # Music / Spotify
    if any(k in text for k in ["spotify", "music", "playlist", "podcast", "apple music"]):
        add({
            "id": "music_platform",
            "question": "What music or podcast platform do you use?",
            "type": "choice",
            "options": ["Spotify", "Apple Music", "YouTube Music", "Other"],
        })

    # Motorsport / F1 / sports fan
    if any(k in text for k in ["f1", "formula 1", "formula one", "motorsport", "sport fan",
                                 "football", "soccer", "rugby", "cricket", "nba", "nfl"]):
        add({
            "id": "sports_interests", "multi": True,
            "question": "Which sports or motorsport series do you follow?",
            "type": "choice",
            "options": ["F1 / Formula 1", "Football / Soccer", "Rugby", "Cricket", "Basketball / NBA", "Other"],
        })

    # Smart home
    if any(k in text for k in ["smart home", "hue", "philips", "govee", "alexa", "homekit",
                                 "google home", "automation"]):
        add({
            "id": "smart_home",
            "question": "What smart home platform do you use?",
            "type": "choice",
            "options": ["Philips Hue", "Google Home", "Amazon Alexa", "Apple HomeKit", "Other"],
        })

    # Crypto / finance
    if any(k in text for k in ["crypto", "bitcoin", "ethereum", "luno", "binance", "kraken",
                                 "coinbase", "trading", "portfolio"]):
        add({
            "id": "crypto_exchange",
            "question": "Which crypto exchange or portfolio tracker do you use?",
            "type": "choice",
            "options": ["Luno", "Binance", "Kraken", "Coinbase", "CoinGecko", "Other"],
        })

    return questions


def generate_suggestions(
    role_text: str, detected_role: str, profile: dict
) -> list[dict]:
    """Generate 20-30 notification suggestions tailored to the user's role.

    In Mode B/C (LLM available): calls openclaw agent to generate personalised suggestions.
    In Mode A (no LLM): generates from the role profile's key_triggers + category extras.

    Returns list of dicts:
        [{"title": "...", "description": "...", "category": "...",
          "priority": "high|medium|low", "pre_checked": bool,
          "required_skill": str|None}]
    """
    # Determine LLM availability
    agent_available = _check_agent_available()

    if agent_available and role_text:
        suggestions = _generate_with_llm(role_text, detected_role, profile)
        if suggestions and len(suggestions) >= 10:
            return suggestions

    # Fallback: Mode A -- generate from profile data
    return _generate_from_profile(detected_role, profile)


def generate_suggestions_with_context(
    role_text: str, detected_role: str, answers: dict
) -> list[dict]:
    """Generate suggestions using follow-up answers for better category mapping.

    The answers dict maps question IDs to user selections, e.g.:
        {"ticket_tool": "Linear", "repo_tool": "GitHub"}

    These answers inform the LLM prompt so it assigns correct categories
    instead of dumping everything into 'email'.
    """
    profile = _get_profile(detected_role)
    agent_available = _check_agent_available()

    if agent_available and role_text:
        suggestions = _generate_with_agent_context(role_text, detected_role, profile, answers)
        if suggestions and len(suggestions) >= 10:
            suggestions = _apply_answer_overrides(suggestions, answers)
            suggestions = _fix_tool_skill_assignments(suggestions)
            return _mark_build_needed(suggestions)

    # Fallback: generate from profile + apply answer-based overrides
    suggestions = _generate_from_profile(detected_role, profile)
    suggestions = _apply_answer_overrides(suggestions, answers)
    suggestions = _fix_tool_skill_assignments(suggestions)
    return _mark_build_needed(suggestions)


def _generate_with_agent_context(
    role_text: str, detected_role: str, profile: dict, answers: dict
) -> list[dict]:
    """Use openclaw agent to generate suggestions with tool-answer context."""
    visible_cats = profile.get("visible_categories", [])
    label = profile.get("label", detected_role)
    cats_str = ", ".join(visible_cats) if visible_cats else ", ".join(ALL_CATEGORIES)

    # Build context from answers -- include all question answers verbatim
    _ANSWER_LABELS = {
        "ticket_tool": "issue tracking / QA tool",
        "community_platform": "community platform",
        "client_tool": "client project tracking tool",
        "repo_tool": "code repository",
        "personal_project_tool": "personal project tracking tool",
        "calendar_tool": "calendar / scheduling tool",
        "email_client": "email client",
        "finance_tool": "invoicing / accounting tool",
        "crm_tool": "CRM / sales tool",
        "social_platform": "social media platform(s)",
        "gaming_platform": "gaming platform(s)",
        "travel_tool": "travel planning tool",
        "health_tool": "health / fitness tracker",
        "music_platform": "music / podcast platform",
        "sports_interests": "sports / motorsport interests",
        "smart_home": "smart home platform",
        "crypto_exchange": "crypto exchange / portfolio tracker",
    }
    answer_lines = []
    for qid, answer in answers.items():
        label = _ANSWER_LABELS.get(qid, qid.replace("_", " "))
        # Multi-select answers are lists -- join for readability
        display = ", ".join(answer) if isinstance(answer, list) else answer
        answer_lines.append(f"- {label}: {display}")
    context_block = "\n".join(answer_lines) if answer_lines else "No additional tool info."

    # Load relevant research files for richer context
    research_content = _load_relevant_research(role_text, detected_role)
    research_block = ""
    if research_content:
        research_block = (
            f"\n\nReference material (role-specific notification patterns and required skills):\n"
            f"<research>\n{research_content}\n</research>\n\n"
            f"IMPORTANT: Use the research above to:\n"
            f"1. Identify exact clawhub skill slugs for each suggestion (e.g. \"linear\" not \"github\" for Linear tasks)\n"
            f"2. For tools/services that have NO matching clawhub skill, set required_skill to \"__build_needed__\" "
            f"and note in the description that the user should ask their OpenClaw agent to build a skill for it\n"
            f"3. Be extremely precise — use the actual tool name the user mentioned, not a generic alternative\n"
        )

    prompt = (
        f"You are setting up a proactive notification assistant for someone.\n\n"
        f"They described themselves as: \"{role_text}\"\n"
        f"Their role: {label}\n\n"
        f"Additional context from follow-up questions:\n{context_block}\n"
        f"{research_block}\n"
        f"Generate exactly 25 notification suggestions that are genuinely useful for this specific person.\n\n"
        f"For EACH suggestion, work through this reasoning before writing it:\n"
        f"  1. What is the trigger? (what event or state change fires this?)\n"
        f"  2. Where does that data actually live? Be precise.\n"
        f"  3. Does an OpenClaw skill already exist for that exact data source?\n"
        f"     Known skills and what they can actually READ/query:\n"
        f"     - gog: Gmail inbox + Google Calendar. Use for: email alerts, AND any time-based reminder\n"
        f"       that could live in a calendar (recurring meetings, sports schedules, race weekends,\n"
        f"       weekly prompts, annual reminders). If it's a scheduled or recurring event, use gog.\n"
        f"     - github: GitHub only — PRs, issues, CI/CD, commits, repo activity. NOT for other git hosts.\n"
        f"     - linear: Linear only — tickets, sprints, milestones, assignments, issue status.\n"
        f"       Use 'linear' for ANY notification that reads from Linear (overnight checks, milestone alerts,\n"
        f"       stale tickets, QA sign-offs, sprint reviews). Do NOT mark Linear-based alerts as build_needed.\n"
        f"     - slack: Slack only — messages, mentions, channel alerts. NOT Discord, NOT Teams.\n"
        f"       NEVER assign 'discord' to a Slack notification. They are different products.\n"
        f"     - discord: Discord only — messages, mentions, server events. NOT Slack.\n"
        f"     - weather: weather forecasts and severe weather alerts.\n"
        f"     - healthcheck: Apple Health metrics (steps, heart rate, sleep, etc).\n"
        f"     - spotify-player: Spotify playback and library.\n"
        f"     - tripit: TripIt travel itineraries.\n"
        f"     - openhue: Philips Hue smart lights.\n"
        f"     - null (built-in): Use for pure time-based prompts with NO external data source needed.\n"
        f"       e.g. 'Every Wednesday prompt to set a launch date' — no API needed, just a scheduled alert.\n"
        f"  4. Use '__build_needed__' ONLY when data requires:\n"
        f"     - Scraping a live website (breaking news, live scores, real-time prices)\n"
        f"     - RSS feeds, Reddit, YouTube, Twitter/X, Twitch, game studio news\n"
        f"     - Any API not in the list above\n"
        f"     - SSL cert monitoring, DNS, uptime checks\n"
        f"     DO NOT use build_needed for: Linear alerts, Slack alerts, calendar-based schedules,\n"
        f"     or recurring time-based prompts that need no external data.\n\n"
        f"Available categories: {cats_str}\n\n"
        f"Category rules:\n"
        f"- 'dev': tool-specific (Linear, GitHub, Jira, GitLab, CI/CD, PRs, deploys)\n"
        f"- 'calendar': scheduling, meetings, deadlines, reminders tied to time\n"
        f"- 'finance': invoicing, payments, billing\n"
        f"- 'system': platform health, uptime, moderation\n"
        f"- 'email': ONLY for literal email inbox notifications\n"
        f"- 'social': reviews, mentions, community posts\n"
        f"- 'compliance': licence/cert renewals, legal deadlines\n\n"
        f"Return ONLY a JSON array. Each item must have exactly these keys:\n"
        f'- "title": short notification title (3-8 words, specific to their role)\n'
        f'- "description": one sentence — what fires this and what data source powers it\n'
        f'- "category": one of [{cats_str}]\n'
        f'- "priority": "high", "medium", or "low"\n'
        f'- "pre_checked": true for high/medium priority, false for low\n'
        f'- "required_skill": exact skill slug from the known list, or "__build_needed__" if not covered, or null if built-in\n\n'
        f"Include 8-10 high, 10-12 medium, 5-8 low priority suggestions.\n"
        f"Be specific to this person — not generic. Output ONLY the JSON array."
    )

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--session-id", "moltassist-onboard", "-m", prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode != 0:
            return []

        output = result.stdout.strip()
        start = output.find("[")
        end = output.rfind("]")
        if start == -1 or end == -1:
            return []

        raw = json.loads(output[start:end + 1])
        suggestions = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            _cat = _remap_category(
                str(item.get("title", "")),
                str(item.get("description", "")),
                str(item.get("category", "custom")),
            )
            # Prefer LLM-provided required_skill when research is present
            llm_skill = item.get("required_skill")
            if isinstance(llm_skill, str) and llm_skill:
                skill = llm_skill
            else:
                skill = _CATEGORY_SKILL_MAP.get(_cat, None)
            s = {
                "title": str(item.get("title", "")),
                "description": str(item.get("description", "")),
                "category": _cat,
                "priority": str(item.get("priority", "medium")),
                "pre_checked": bool(item.get("pre_checked", True)),
                "required_skill": skill,
            }
            if s["priority"] not in ("high", "medium", "low"):
                s["priority"] = "medium"
            suggestions.append(s)

        return suggestions

    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        return []


def _remap_category(title: str, description: str, category: str) -> str:
    """Post-process LLM category assignments to fix common mistakes.
    The LLM tends to assign 'email' to everything. This corrects it."""
    text = (title + " " + description).lower()
    # Dev tools → dev category
    if any(k in text for k in ["linear", "github", "gitlab", "jira", "pr ", "pull request",
                                 "deploy", "ci/cd", "commit", "branch", "issue tracker",
                                 "bug report", "ticket", "sprint", "backlog", "release milestone"]):
        return "dev"
    # Community/moderation → social category (requires discord/slack skill)
    if any(k in text for k in ["discord", "slack", "moderat", "community", "member",
                                 "flagged", "reported", "escalation"]):
        return "social"
    # Scheduling/time → calendar
    if any(k in text for k in ["meeting", "standup", "demo", "review", "reminder",
                                 "schedule", "deadline", "due date", "before ", "prep"]):
        if category == "email":
            return "calendar"
    # Finance stays finance
    if any(k in text for k in ["invoice", "payment", "billing", "expense", "contract",
                                 "rate ", "freelance invoice", "overdue"]):
        return "finance"
    # Daily prompts/checklists that aren't calendar events → system (no skill needed)
    if any(k in text for k in ["daily", "run-through", "usability", "bug check", "end of day",
                                 "each day", "every day"]):
        if category in ("email", "custom"):
            return "system"
    return category


# Map tool answers to category overrides
_ANSWER_CATEGORY_MAP = {
    "ticket_tool": "dev",
    "repo_tool": "dev",
    "community_platform": "system",
    "client_tool": "finance",
}


def _resolve_answer_skill(answer) -> str | list[str] | None:
    """Resolve an answer string (or list) to a skill slug or list of slugs.

    For single answers: returns a string slug or None.
    For multi-select lists: returns a list of all distinct slugs found (may be empty list).
    This allows a single category to require multiple skills (e.g. Slack + Discord).
    """
    if not answer:
        return None
    if isinstance(answer, list):
        slugs = []
        seen = set()
        for item in answer:
            slug = _resolve_answer_skill(item)
            if slug and slug not in seen and slug != "__build_needed__":
                slugs.append(slug)
                seen.add(slug)
        return slugs if slugs else None
    key = answer.lower().strip()
    if key in _TOOL_SKILL_MAP:
        return _TOOL_SKILL_MAP[key]
    return _fuzzy_match_tool_to_skill(key)


def _apply_answer_overrides(suggestions: list[dict], answers: dict) -> list[dict]:
    """Apply answer-based category corrections and skill assignments.

    Uses all answers (ticket_tool, community_platform, personal_project_tool,
    gaming_platform, travel_tool, crypto_exchange, etc.) to assign the correct
    skill slug to each suggestion. Supports freeform 'Other' values via fuzzy matching.
    """
    if not answers:
        return suggestions

    for s in suggestions:
        title_lower = s["title"].lower()
        desc_lower = s["description"].lower()
        combined = title_lower + " " + desc_lower

        # Issue tracking / dev tool
        if "ticket_tool" in answers:
            skill = _resolve_answer_skill(answers["ticket_tool"])
            if s["category"] == "dev":
                s["required_skill"] = skill

        # Community platform — multi-select: user may have Slack + Discord + Reddit etc.
        if "community_platform" in answers:
            skill = _resolve_answer_skill(answers["community_platform"])
            if s["category"] == "social":
                # If multiple platforms selected, store as list so UI can show multiple badges
                s["required_skill"] = skill if skill else None

        # Code repo tool
        if "repo_tool" in answers:
            skill = _resolve_answer_skill(answers["repo_tool"])
            if any(kw in combined for kw in ["repo", "commit", "deploy", "ci/cd", "merge", "pull request"]):
                s["category"] = "dev"
                s["required_skill"] = skill

        # Personal project tracking
        if "personal_project_tool" in answers:
            skill = _resolve_answer_skill(answers["personal_project_tool"])
            if any(kw in combined for kw in ["personal project", "side project", "launch", "stalled", "project idea"]):
                s["required_skill"] = skill

        # Client / freelance tracking
        if "client_tool" in answers:
            if any(kw in combined for kw in ["invoice", "payment", "client", "billing", "contract"]):
                s["category"] = "finance"
                s["required_skill"] = None

        # Calendar tool
        if "calendar_tool" in answers:
            skill = _resolve_answer_skill(answers["calendar_tool"])
            if s["category"] == "calendar":
                s["required_skill"] = skill

        # Finance tool
        if "finance_tool" in answers:
            skill = _resolve_answer_skill(answers["finance_tool"])
            if s["category"] == "finance" and skill:
                s["required_skill"] = skill

        # CRM
        if "crm_tool" in answers:
            skill = _resolve_answer_skill(answers["crm_tool"])
            if any(kw in combined for kw in ["crm", "lead", "sales", "customer", "pipeline"]):
                s["required_skill"] = skill

        # Health / fitness
        if "health_tool" in answers:
            skill = _resolve_answer_skill(answers["health_tool"])
            if s["category"] == "health":
                s["required_skill"] = skill

        # Music
        if "music_platform" in answers:
            skill = _resolve_answer_skill(answers["music_platform"])
            if any(kw in combined for kw in ["music", "playlist", "podcast", "spotify"]):
                s["required_skill"] = skill

        # Crypto
        if "crypto_exchange" in answers:
            skill = _resolve_answer_skill(answers["crypto_exchange"])
            if any(kw in combined for kw in ["crypto", "bitcoin", "portfolio", "exchange", "price"]):
                s["required_skill"] = skill

        # Travel
        if "travel_tool" in answers:
            skill = _resolve_answer_skill(answers["travel_tool"])
            if any(kw in combined for kw in ["travel", "trip", "flight", "hotel", "passport", "visa", "booking"]):
                s["required_skill"] = skill

        # Smart home
        if "smart_home" in answers:
            skill = _resolve_answer_skill(answers["smart_home"])
            if any(kw in combined for kw in ["smart home", "lights", "hue", "automation", "home"]):
                s["required_skill"] = skill

    return suggestions


def _fix_tool_skill_assignments(suggestions: list[dict]) -> list[dict]:
    """Post-processing pass: override required_skill based on tool mentions in title/description.

    The LLM sometimes marks tool-specific alerts (Linear, Slack, GitHub, etc.) as
    build_needed when the skill already exists. This corrects those cases definitively.
    Tool mentions in the text are ground truth — the named skill IS available for that tool.
    """
    # Map of text signals → correct skill slug
    # Ordered most-specific first
    _TOOL_SIGNAL_MAP: list[tuple[list[str], str]] = [
        (["linear"], "linear"),
        (["github", "gh ", "pull request", "pr review", "ci/cd", "ci failure", "pipeline fail"], "github"),
        (["gitlab"], "gitlab"),
        (["slack"], "slack"),
        (["discord"], "discord"),
        (["jira"], "jira"),
        (["notion"], "notion"),
        (["trello"], "trello"),
        (["asana"], "asana"),
        (["clickup"], "clickup"),
        (["spotify"], "spotify-player"),
        (["tripit", "trip it"], "tripit"),
        (["philips hue", "openhue"], "openhue"),
        (["apple health", "healthkit"], "healthcheck"),
        (["strava"], "strava"),
        (["google calendar", "gcal", "g calendar"], "gog"),
        (["gmail", "google mail"], "gog"),
    ]

    for s in suggestions:
        combined = (s.get("title", "") + " " + s.get("description", "")).lower()
        for signals, skill in _TOOL_SIGNAL_MAP:
            if any(sig in combined for sig in signals):
                # Only override if the LLM got it wrong (build_needed or wrong skill)
                if s.get("required_skill") == "__build_needed__" or s.get("required_skill") != skill:
                    s["required_skill"] = skill
                    s["build_needed"] = False
                break  # first match wins

    return suggestions


def _mark_build_needed(suggestions: list[dict]) -> list[dict]:
    """Flag suggestions whose required_skill is '__build_needed__'.

    Also auto-detects suggestions that should be build_needed based on
    their content (news feeds, Reddit, RSS, web scraping, game announcements,
    social platform monitoring) even if the LLM incorrectly assigned a skill.

    Sets build_needed=True and appends a note to the description.
    """
    # Signals that indicate a custom skill/script is needed to get this data
    _BUILD_NEEDED_SIGNALS = [
        "breaking news", "news alert", "reddit", "subreddit", "rss", "feed",
        "ign.com", "game announcement", "game news", "trailer", "release date", "patch notes",
        "rockstar", "game studio", "steam news", "xbox news", "playstation news",
        "scrape", "crawl", "monitor website", "ssl cert", "ssl certificate",
        "uptime", "dns ", "website down", "web search",
        "youtube alert", "twitch alert", "twitter alert", "x alert", "instagram alert",
        "reddit post", "forum post", "community post", "news story",
        "new trailer", "release update", "launch date", "announced",
    ]

    suffix = "(ask OpenClaw to build this skill)"
    for s in suggestions:
        combined = (s.get("title", "") + " " + s.get("description", "")).lower()

        # Auto-flag if content signals build_needed — but NOT if _fix_tool_skill_assignments
        # already resolved it to a known skill (build_needed explicitly set to False)
        if any(sig in combined for sig in _BUILD_NEEDED_SIGNALS) and s.get("build_needed") is not False:
            s["required_skill"] = "__build_needed__"

        if s.get("required_skill") == "__build_needed__":
            s["build_needed"] = True
            if suffix not in s.get("description", ""):
                s["description"] = s["description"].rstrip() + " " + suffix
        else:
            s.setdefault("build_needed", False)
    return suggestions


def _check_agent_available() -> bool:
    """Check if openclaw agent is available."""
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--session-id", "moltassist-probe", "-m", "respond with just: ok"],
            capture_output=True, text=True, timeout=15,
        )
        return result.returncode == 0 and "ok" in result.stdout.lower()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _generate_with_llm(
    role_text: str, detected_role: str, profile: dict
) -> list[dict]:
    """Use openclaw agent to generate personalised suggestions."""
    visible_cats = profile.get("visible_categories", [])
    key_triggers = profile.get("key_triggers", [])
    label = profile.get("label", detected_role)
    cats_str = ", ".join(visible_cats) if visible_cats else ", ".join(ALL_CATEGORIES)

    prompt = (
        f"You are setting up a proactive notification assistant for someone.\n\n"
        f"They described themselves as: \"{role_text}\"\n"
        f"Their role: {label}\n\n"
        f"Generate exactly 25 notification suggestions that are genuinely useful for this specific person.\n"
        f"Think about:\n"
        f"- Their daily rhythm (what happens every morning, weekly, monthly)\n"
        f"- What they need to know BEFORE key tasks or meetings\n"
        f"- Time-sensitive triggers specific to their work\n"
        f"- What follow-ups they typically forget\n\n"
        f"Available categories: {cats_str}\n\n"
        f"Return ONLY a JSON array. Each item must have exactly these keys:\n"
        f'- "title": short notification title (3-8 words, specific to their role)\n'
        f'- "description": one sentence explaining exactly when/why this fires\n'
        f'- "category": one of [{cats_str}]\n'
        f'- "priority": "high", "medium", or "low"\n'
        f'- "pre_checked": true for high/medium priority, false for low\n\n'
        f"Include 8-10 high, 10-12 medium, 5-8 low priority suggestions.\n"
        f"Be specific to their role — not generic. Output ONLY the JSON array."
    )

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--session-id", "moltassist-onboard", "-m", prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode != 0:
            return []

        # Extract JSON from response
        output = result.stdout.strip()
        # Try to find JSON array in the output
        start = output.find("[")
        end = output.rfind("]")
        if start == -1 or end == -1:
            return []

        raw = json.loads(output[start:end + 1])
        suggestions = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            _cat = _remap_category(
                str(item.get("title", "")),
                str(item.get("description", "")),
                str(item.get("category", "custom")),
            )
            s = {
                "title": str(item.get("title", "")),
                "description": str(item.get("description", "")),
                "category": _cat,
                "priority": str(item.get("priority", "medium")),
                "pre_checked": bool(item.get("pre_checked", True)),
                "required_skill": _CATEGORY_SKILL_MAP.get(_cat, None),
            }
            if s["priority"] not in ("high", "medium", "low"):
                s["priority"] = "medium"
            suggestions.append(s)

        return suggestions

    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        return []


def _generate_from_profile(detected_role: str, profile: dict) -> list[dict]:
    """Generate suggestions from role profile key_triggers + category extras.

    Falls back to this when no LLM is available (Mode A).
    """
    suggestions = []
    visible_cats = set(profile.get("visible_categories", []))
    key_triggers = profile.get("key_triggers", [])
    urgency_defaults = profile.get("urgency_defaults", {})

    # 1. Generate from key_triggers
    for trigger in key_triggers:
        template = _TRIGGER_TEMPLATES.get(trigger)
        if template:
            s = dict(template)
            s["required_skill"] = _CATEGORY_SKILL_MAP.get(s["category"])
            s["pre_checked"] = s["priority"] in ("high", "medium")
            suggestions.append(s)
        else:
            # Generate a basic suggestion from the trigger name
            title = trigger.replace("_", " ").title()
            cat = _guess_category_for_trigger(trigger, visible_cats)
            priority = urgency_defaults.get(cat, "medium")
            if priority not in ("high", "medium", "low"):
                priority = "medium"
            suggestions.append({
                "title": title,
                "description": f"Notification for {trigger.replace('_', ' ')}.",
                "category": cat,
                "priority": priority,
                "pre_checked": priority in ("high", "medium"),
                "required_skill": _CATEGORY_SKILL_MAP.get(cat),
            })

    # 2. Add category extras for visible categories
    seen_titles = {s["title"].lower() for s in suggestions}
    for cat in visible_cats:
        extras = _CATEGORY_EXTRAS.get(cat, [])
        for extra in extras:
            if extra["title"].lower() not in seen_titles:
                s = dict(extra)
                s["category"] = cat
                s["required_skill"] = _CATEGORY_SKILL_MAP.get(cat)
                s["pre_checked"] = s["priority"] in ("high", "medium")
                suggestions.append(s)
                seen_titles.add(s["title"].lower())

    # 3. If we still have fewer than 20, add common cross-role suggestions
    common = [
        {"title": "Morning briefing", "description": "Daily summary of what needs your attention today.", "category": "email", "priority": "medium"},
        {"title": "Quiet hours active", "description": "Confirmation that quiet hours have kicked in.", "category": "email", "priority": "low"},
        {"title": "Weekly summary", "description": "End-of-week recap of all notifications and actions taken.", "category": "email", "priority": "low"},
        {"title": "MoltAssist health check", "description": "Weekly check that all your notification sources are working.", "category": "email", "priority": "low"},
        {"title": "Calendar conflict detected", "description": "Alert when two events overlap on your calendar.", "category": "calendar", "priority": "high"},
        {"title": "Upcoming deadline reminder", "description": "Advance warning for approaching deadlines.", "category": "calendar", "priority": "medium"},
    ]
    for c in common:
        if len(suggestions) >= 30:
            break
        if c["title"].lower() not in seen_titles:
            s = dict(c)
            s["required_skill"] = _CATEGORY_SKILL_MAP.get(s["category"])
            s["pre_checked"] = s["priority"] in ("high", "medium")
            suggestions.append(s)
            seen_titles.add(s["title"].lower())

    # Sort: high first, then medium, then low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: priority_order.get(s["priority"], 1))

    return suggestions


def _guess_category_for_trigger(trigger: str, visible_cats: set) -> str:
    """Guess a category for an unknown trigger based on keywords."""
    trigger_lower = trigger.lower()
    cat_hints = {
        "compliance": ["licence", "license", "cert", "safety", "permit", "insurance", "inspection"],
        "finance": ["invoice", "payment", "cost", "revenue", "stock", "supplier", "billing", "order", "expense"],
        "staff": ["staff", "roster", "timesheet", "no_show"],
        "calendar": ["booking", "event", "deadline", "schedule", "confirmation"],
        "social": ["review", "mention", "social"],
        "email": ["email", "client", "comms"],
        "weather": ["weather", "forecast"],
        "health": ["health", "medication", "step"],
        "dev": ["ci", "deploy", "pr_", "issue", "build"],

    }
    for cat, keywords in cat_hints.items():
        for kw in keywords:
            if kw in trigger_lower:
                if cat in visible_cats:
                    return cat
                return cat
    # Default to first visible category or "custom"
    if visible_cats:
        return sorted(visible_cats)[0]
    return "custom"


def _detect_active_channels() -> list[str]:
    """Detect which channels OpenClaw has active via CLI."""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "channels", "list", "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            import json
            data = json.loads(result.stdout.strip())
            if isinstance(data, list):
                return [c.get("name", c) if isinstance(c, dict) else str(c) for c in data]
            elif isinstance(data, dict):
                # OpenClaw returns {"chat": {"telegram": [...], "whatsapp": [...]}, "auth": [...], ...}
                # Extract actual chat channel names from the "chat" key
                chat = data.get("chat", {})
                if isinstance(chat, dict):
                    return sorted(chat.keys())
                return list(data.keys())
    except Exception:
        pass
    return []


def start_onboarding() -> dict:
    """Returns the first message to send + expected response type.

    If only one channel is configured, skip channel selection and go
    straight to the dashboard. If multiple, ask which to use.
    """
    channels = _detect_active_channels()

    if len(channels) == 1:
        # Single channel -- skip channel question, go to role question (step 2)
        channel = channels[0].lower()
        return {
            "message": (
                f"Welcome to MoltAssist! I'll use {channel.title()} for your notifications.\n\n"
                "What do you do for work -- and what kinds of things catch you off guard?"
            ),
            "buttons": None,
            "step": 2,
            "state": {"channel": channel, "llm_mode": "b"},
            "expects": "text",
        }

    # Multiple channels -- ask which one
    return {
        "message": (
            "Welcome to MoltAssist! Let's get your notifications set up.\n\n"
            "Which channel should MoltAssist use?"
        ),
        "buttons": [c.title() for c in channels] if channels else ["Telegram", "WhatsApp", "Discord"],
        "step": 1,
        "expects": "button",
    }


def process_onboarding_response(step: int, response: str, state: dict) -> dict:
    """Takes user's response to current step, returns next step or completion.

    Returns:
        {
            "message": str,
            "buttons": list | None,
            "step": int,
            "done": bool,
            "config": dict | None,
            "state": dict,
        }
    When done=True, config contains the generated moltassist config.
    """
    state = dict(state)  # don't mutate caller's dict

    if step == 1:
        # Channel selection (only reached when multiple channels configured)
        channel = response.strip().lower()
        if channel not in ("telegram", "whatsapp", "discord"):
            channel = "telegram"
        state["channel"] = channel
        state["llm_mode"] = "b"

        # Proceed to step 2: ask role question
        return {
            "message": (
                f"Got it -- I'll use {channel.title()}.\n\n"
                "What do you do for work -- and what kinds of things catch you off guard?"
            ),
            "buttons": None,
            "step": 2,
            "done": False,
            "config": None,
            "state": state,
            "expects": "text",
        }

    elif step == 2:
        # Role selection
        llm_mode = state.get("llm_mode", "a")

        if llm_mode in ("b", "c"):
            # Free text -- detect role
            role_id = detect_role(response)
            state["role_text"] = response
        else:
            # Button press -- map to role
            role_id = _MODE_A_BUTTON_TO_ROLE.get(response, "fallback")

        state["role_id"] = role_id
        role_text = state.get("role_text", response)
        profile = _get_profile(role_id)

        # Generate suggestions and set up browser onboarding
        suggestions = generate_suggestions(role_text, role_id, profile)
        state["suggestions"] = suggestions

        # Store in server module for the /onboard page
        try:
            from moltassist.server import set_onboard_session
            set_onboard_session(role_text, role_id, suggestions)
        except ImportError:
            pass

        # Start the dashboard server in the background
        try:
            subprocess.Popen(
                ["moltassist", "config"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

        n = len(suggestions)

        return {
            "message": (
                f"I've got {n} suggestions for you. "
                "Open this to review and confirm:\n"
                "http://localhost:7430"
            ),
            "buttons": None,
            "step": "onboard_browser",
            "done": False,
            "config": None,
            "state": state,
        }

    elif step == 3:
        # What matters -- multi-select
        # response is comma-separated button labels
        selections = [s.strip() for s in response.split(",")]
        selected_categories = []
        for sel in selections:
            cat = _MATTER_TO_CATEGORY.get(sel)
            if cat:
                selected_categories.append(cat)
        state["selected_categories"] = selected_categories

        # Step 4: Intelligence pass
        role_id = state.get("role_id", "fallback")
        profile = _get_profile(role_id)

        # Merge: profile visible_categories + user selections
        visible = set(profile.get("visible_categories", []))
        visible.update(selected_categories)
        state["visible_categories"] = sorted(visible)

        # Check required skills
        required_skills = set(profile.get("required_skills", []))
        for cat in visible:
            skill = SKILL_MAP.get(cat)
            if skill:
                required_skills.add(skill)

        state["required_skills"] = sorted(required_skills)

        # Build intelligence summary
        role_label = profile.get("label", "General")
        lines = [f"Based on your role as a {role_label}:"]

        for cat in sorted(visible):
            display = CATEGORY_DISPLAY.get(cat, cat)
            # Apply label overrides from profile
            label_overrides = profile.get("label_overrides", {})
            if cat in label_overrides:
                display = label_overrides[cat]

            skill = SKILL_MAP.get(cat)
            if skill is None:
                lines.append(f"  {display} -- built in")
            else:
                # We don't have actual skill detection here -- that's OpenClaw's job
                # Mark as requiring install
                lines.append(f"  {display} -- requires {skill}")

        if required_skills:
            lines.append(f"\nRequired skills: {', '.join(sorted(required_skills))}")

        lines.append("\nGenerate config now?")

        return {
            "message": "\n".join(lines),
            "buttons": ["Yes, generate config", "Let me adjust"],
            "step": 4,
            "done": False,
            "config": None,
            "state": state,
        }

    elif step == 4:
        # Confirm
        if "adjust" in response.lower() or response.lower() == "no":
            # Go back to step 3
            return {
                "message": "What matters to you? Select all that apply:",
                "buttons": MATTER_BUTTONS,
                "step": 3,
                "done": False,
                "config": None,
                "state": state,
            }

        # Generate config
        config = generate_config_from_onboarding(state)
        state["config"] = config

        # Install scheduler system job
        scheduler_msg = ""
        try:
            from moltassist.scheduler import Scheduler
            workspace = Path(__file__).resolve().parent.parent
            installed = Scheduler().install_system_job(workspace)
            if installed:
                scheduler_msg = (
                    "\nMoltAssist scheduler installed -- checking in the background automatically."
                )
            else:
                scheduler_msg = (
                    "\nScheduler install failed. To install manually, run:\n"
                    f"  /moltassist scheduler install"
                )
        except Exception:
            scheduler_msg = (
                "\nScheduler install skipped. To install manually, run:\n"
                "  /moltassist scheduler install"
            )

        return {
            "message": (
                "Done! Your MoltAssist config has been generated.\n"
                "Run `/moltassist config` to open the settings panel and fine-tune anytime."
                + scheduler_msg
            ),
            "buttons": None,
            "step": 5,
            "done": True,
            "config": config,
            "state": state,
        }

    # Unknown step
    return {
        "message": "Something went wrong. Please run /moltassist onboard again.",
        "buttons": None,
        "step": step,
        "done": True,
        "config": None,
        "state": state,
    }


def generate_config_from_onboarding(state: dict) -> dict:
    """Takes completed onboarding state, returns full config.json structure.

    Maps role -> visible categories, sets urgency defaults, sets llm_enrich per category.
    """
    role_id = state.get("role_id", "fallback")
    profile = _get_profile(role_id)

    channel = state.get("channel", "telegram")
    visible = state.get("visible_categories", profile.get("visible_categories", []))

    # Build categories config
    categories = {}
    for cat in ALL_CATEGORIES:
        enabled = cat in visible
        llm_enrich = profile.get("llm_enrich_defaults", {}).get(cat, False) if enabled else False

        # Get display label (with overrides)
        label = CATEGORY_DISPLAY.get(cat, cat)
        label_overrides = profile.get("label_overrides", {})
        if cat in label_overrides:
            label = label_overrides[cat]

        # Get urgency default
        urgency = profile.get("urgency_defaults", {}).get(cat, "medium")

        categories[cat] = {
            "enabled": enabled,
            "label": label,
            "urgency": urgency,
            "llm_enrich": llm_enrich,
        }

    # Build config
    config = {
        "version": "0.1",
        "role": role_id,
        "delivery": {
            "default_channel": channel,
            "urgency_routing": {
                "critical": channel,
                "high": channel,
                "medium": channel,
                "low": channel,
            },
            "channels": {
                "telegram": {"active": channel == "telegram", "chat_id": state.get("telegram_chat_id", "")},
                "whatsapp": {"active": channel == "whatsapp", "target": state.get("whatsapp_target", "")},
                "discord":  {"active": channel == "discord",  "target": state.get("discord_target", "")},
            },
        },
        "categories": categories,
        "schedule": {
            "quiet_hours": {"start": "23:00", "end": "08:00"},
            "timezone": "UTC",
            "morning_digest": True,
            "rate_limits": {
                "per_category_per_hour": 3,
                "global_per_hour": 10,
            },
        },
        "urgency_threshold": "medium",
        "required_skills": profile.get("required_skills", []),
        "key_triggers": profile.get("key_triggers", []),
    }

    return config
