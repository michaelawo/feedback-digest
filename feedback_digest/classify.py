"""Put each message into a category using keyword lists."""
import re

# Whole words only. Variants are listed on purpose: matching on the start of
# a word looks clever but "pass" would then match "passenger".
KEYWORDS = {
    "delay": {
        "late", "delay", "delays", "delayed", "waited", "waiting", "wait",
        "cancelled", "canceled", "missed", "minutes", "punctual",
    },
    "crowding": {"crowded", "overcrowded", "packed", "full", "squeezed", "cramped"},
    "cleanliness": {
        "dirty", "filthy", "smell", "smells", "smelly", "rubbish", "litter",
        "graffiti", "sticky", "unclean", "cleaned",
    },
    "staff": {
        "driver", "drivers", "inspector", "inspectors", "rude", "staff",
        "shouted", "helpful", "polite", "unfriendly",
    },
    "ticketing": {
        "ticket", "tickets", "pass", "machine", "app", "fined", "fine",
        "refund", "validator", "payment", "card", "charged",
    },
    "accessibility": {
        "wheelchair", "ramp", "lift", "elevator", "escalator", "escalators",
        "pram", "stroller", "accessible", "step", "steps",
    },
    "information": {
        "display", "displays", "announcement", "announcements", "timetable",
        "sign", "signs", "information", "map", "screen", "screens",
    },
    "safety": {
        "unsafe", "dangerous", "braked", "braking", "accident", "slippery",
        "fell", "injured", "fight", "harassed",
    },
}
CATEGORIES = list(KEYWORDS) + ["other"]


def classify(text):
    """Return the category with the most matching words, or 'other'."""
    words = re.findall(r"[a-z]+", text.lower())
    best, best_hits = "other", 0
    for category, keywords in KEYWORDS.items():
        hits = sum(1 for w in words if w in keywords)
        if hits > best_hits:
            best, best_hits = category, hits
    return best


def classify_all(items):
    for item in items:
        item.category = classify(item.text)
