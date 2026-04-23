from app.config import USE_PROVIDER
from app.services.sheets_service import log_event_sheets
from datetime import datetime
import json

def log_event(event_type, restaurant_id, payload):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "restaurant_id": restaurant_id,
        "payload": payload
    }

    print(json.dumps(record, ensure_ascii=False))

    if USE_PROVIDER == "sheets":
        try:
            log_event_sheets(event_type, restaurant_id, payload)
        except Exception as e:
            print(f"Sheet log error: {e}")

    return record