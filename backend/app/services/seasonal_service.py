import json
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "data" / "seasonal_rules.json"

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_seasonal_context(restaurant_id, date):
    rules = load_rules()
    return {
        "restaurant_id": restaurant_id,
        "date": date,
        "seasonal_rules": rules
    }