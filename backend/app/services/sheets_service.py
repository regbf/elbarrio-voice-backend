import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SHEETS_FILE, GOOGLE_CREDENTIALS_FILE
from datetime import datetime
import uuid

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_client()
    workbook = client.open(GOOGLE_SHEETS_FILE)
    return workbook.worksheet(sheet_name)

def ensure_sheet_exists(sheet_name, headers):
    client = get_client()
    workbook = client.open(GOOGLE_SHEETS_FILE)
    try:
        ws = workbook.worksheet(sheet_name)
    except:
        ws = workbook.add_worksheet(title=sheet_name, rows="1000", cols=str(len(headers)))
        ws.append_row(headers)
    return ws

def setup_default_sheets():
    ensure_sheet_exists("reservations", [
        "booking_id", "restaurant_id", "name", "phone", "date", "time",
        "party_size", "seating_preference", "occasion", "notes", "status",
        "language", "channel", "created_at", "updated_at"
    ])
    ensure_sheet_exists("orders", [
        "order_id", "restaurant_id", "name", "phone", "date", "requested_time",
        "order_type", "items", "notes", "status", "language", "channel", "created_at"
    ])
    ensure_sheet_exists("leads", [
        "lead_id", "restaurant_id", "contact_name", "phone", "date",
        "guest_count", "event_type", "notes", "status", "created_at"
    ])
    ensure_sheet_exists("logs", [
        "timestamp", "event_type", "restaurant_id", "payload"
    ])
    ensure_sheet_exists("analytics", [
        "timestamp", "metric", "restaurant_id", "value", "meta"
    ])

def check_availability_sheets(date, time, party_size):
    ws = get_sheet("reservations")
    rows = ws.get_all_records()
    confirmed = [
        r for r in rows
        if r["date"] == date and r["time"] == time and r["status"] == "confirmed"
    ]
    occupied = sum(int(r["party_size"]) for r in confirmed if r["party_size"])
    max_cap = 80
    if occupied + int(party_size) <= max_cap:
        return {"available": True, "alternatives": []}
    return {
        "available": False,
        "alternatives": [
            {"time": "19:30", "available": True},
            {"time": "20:45", "available": True},
            {"time": "21:15", "available": True}
        ]
    }

def create_booking_sheets(payload):
    ws = get_sheet("reservations")
    booking_id = f"EB-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()
    row = [
        booking_id,
        payload.get("restaurant_id"),
        payload.get("name"),
        payload.get("phone"),
        payload.get("date"),
        payload.get("time"),
        payload.get("party_size"),
        payload.get("seating_preference"),
        payload.get("occasion"),
        payload.get("notes"),
        "confirmed",
        payload.get("language"),
        payload.get("channel"),
        now,
        now
    ]
    ws.append_row(row)
    return {"booking_id": booking_id, "status": "confirmed", "created_at": now}

def find_booking_sheets(name, phone_or_reference=None):
    ws = get_sheet("reservations")
    rows = ws.get_all_records()
    for r in rows:
        if str(r["name"]).lower() == name.lower():
            if not phone_or_reference:
                return r
            if r["phone"] == phone_or_reference or r["booking_id"] == phone_or_reference:
                return r
    return None

def create_order_sheets(payload):
    ws = get_sheet("orders")
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()
    row = [
        order_id,
        payload.get("restaurant_id"),
        payload.get("name"),
        payload.get("phone"),
        payload.get("date"),
        payload.get("requested_time"),
        payload.get("order_type"),
        payload.get("items"),
        payload.get("notes"),
        "requested",
        payload.get("language"),
        payload.get("channel"),
        now
    ]
    ws.append_row(row)
    return {"order_id": order_id, "status": "requested", "created_at": now}

def create_group_lead_sheets(payload):
    ws = get_sheet("leads")
    lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()
    row = [
        lead_id,
        payload.get("restaurant_id"),
        payload.get("contact_name"),
        payload.get("phone"),
        payload.get("date"),
        payload.get("guest_count"),
        payload.get("event_type"),
        payload.get("notes"),
        "open",
        now
    ]
    ws.append_row(row)
    return {"lead_id": lead_id, "status": "open", "created_at": now}

def log_event_sheets(event_type, restaurant_id, payload):
    ws = get_sheet("logs")
    ws.append_row([
        datetime.utcnow().isoformat(),
        event_type,
        restaurant_id,
        str(payload)
    ])

def track_metric_sheets(metric, restaurant_id, value=1, meta=None):
    ws = get_sheet("analytics")
    ws.append_row([
        datetime.utcnow().isoformat(),
        metric,
        restaurant_id,
        value,
        str(meta or {})
    ])