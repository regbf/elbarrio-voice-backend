from app.config import USE_PROVIDER
from app.services.fallback_db import create_group_lead_db, create_order_db
from app.services.sheets_service import create_group_lead_sheets, create_order_sheets

def create_group_lead(payload):
    if USE_PROVIDER == "sheets":
        return create_group_lead_sheets(payload)
    return create_group_lead_db(payload)

def create_order_request(payload):
    if USE_PROVIDER == "sheets":
        return create_order_sheets(payload)
    return create_order_db(payload)

def handoff_to_staff(restaurant_id, reason):
    return {
        "success": True,
        "restaurant_id": restaurant_id,
        "handoff": True,
        "reason": reason
    }