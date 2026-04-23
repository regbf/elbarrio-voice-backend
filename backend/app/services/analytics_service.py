from datetime import datetime
from app.config import USE_PROVIDER
from app.services.sheets_service import track_metric_sheets

ANALYTICS_MEMORY = []

def track_metric(metric, restaurant_id, value=1, meta=None):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "metric": metric,
        "restaurant_id": restaurant_id,
        "value": value,
        "meta": meta or {}
    }

    ANALYTICS_MEMORY.append(record)
    print(record)

    if USE_PROVIDER == "sheets":
        try:
            track_metric_sheets(metric, restaurant_id, value, meta)
        except Exception as e:
            print(f"Analytics sheet error: {e}")

    return record

def get_metrics_summary():
    summary = {}
    for r in ANALYTICS_MEMORY:
        metric = r["metric"]
        summary[metric] = summary.get(metric, 0) + r["value"]
    return summary