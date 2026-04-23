import json
from pathlib import Path

KB_PATH = Path(__file__).parent.parent / "data" / "restaurant_kb.json"

def load_kb():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def query_kb(restaurant_id, query):
    kb = load_kb()
    return {
        "restaurant_id": restaurant_id,
        "query": query,
        "data": kb
    }