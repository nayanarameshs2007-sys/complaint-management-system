"""
AI Complaint Analysis Module (Rule & Keyword Based)
This module is isolated so it can be swapped with ML models or LLMs later.
"""

# Category -> (Keywords, Department, Base Priority)
RULE_MAPPING = [
    {
        "category": "Electrical Hazard",
        "department": "Electrical Department",
        "keywords": ["spark", "sparking", "live wire", "broken wire", "hanging wire", "electric shock", "short circuit"],
        "default_priority": "CRITICAL"
    },
    {
        "category": "Road Damage",
        "department": "Public Works",
        "keywords": ["pothole", "road", "asphalt", "crater", "caved in", "broken road", "bridge", "divider"],
        "default_priority": "HIGH"
    },
    {
        "category": "Water Supply & Sewage",
        "department": "Water Authority",
        "keywords": ["water", "leak", "pipe", "overflow", "sewage", "drain", "drainage", "no water", "contaminated"],
        "default_priority": "HIGH"
    },
    {
        "category": "Waste Management",
        "department": "Sanitation",
        "keywords": ["garbage", "trash", "dump", "waste", "smell", "stink", "litter", "cleaning", "dustbin"],
        "default_priority": "MEDIUM"
    },
    {
        "category": "Street Lighting",
        "department": "Electrical Department",
        "keywords": ["streetlight", "street light", "darkness", "lamp", "light bulb", "light pole"],
        "default_priority": "MEDIUM"
    },
    {
        "category": "Public Safety / Obstruction",
        "department": "Traffic & Safety",
        "keywords": ["fallen tree", "blockage", "accident", "signal", "traffic light", "stray animal", "dog"],
        "default_priority": "HIGH"
    }
]

# Keywords that elevate priority to CRITICAL or HIGH
CRITICAL_TRIGGERS = ["emergency", "danger", "dangerous", "hazard", "fire", "spark", "accident", "injured", "risk"]
HIGH_TRIGGERS = ["huge", "large", "overflowing", "blocking", "heavy", "school", "hospital", "urgent"]

def analyze_complaint(description: str, location: str = "") -> dict:
    """
    Analyzes complaint text and determines:
    - Category
    - Assigned Department
    - Priority Level (CRITICAL, HIGH, MEDIUM, LOW)
    """
    text_lower = (description + " " + location).lower()

    detected_category = "General Grievance"
    detected_department = "Municipal Administration"
    detected_priority = "LOW"
    matched_score = 0

    # Match category based on keywords
    for rule in RULE_MAPPING:
        matches = sum(1 for kw in rule["keywords"] if kw in text_lower)
        if matches > matched_score:
            matched_score = matches
            detected_category = rule["category"]
            detected_department = rule["department"]
            detected_priority = rule["default_priority"]

    # Priority boosting logic
    if any(trigger in text_lower for trigger in CRITICAL_TRIGGERS):
        detected_priority = "CRITICAL"
    elif any(trigger in text_lower for trigger in HIGH_TRIGGERS) and detected_priority not in ["CRITICAL", "HIGH"]:
        detected_priority = "HIGH"

    return {
        "category": detected_category,
        "department": detected_department,
        "priority": detected_priority
    }
