import uuid
from datetime import datetime

BOOKINGS = []
ORDERS = []
LEADS = []
MAX_CAPACITY = 80

def check_availability_db(date, time, party_size):
    same_slot = [
        b for b in BOOKINGS
        if b["date"] == date and b["time"] == time and b["status"] == "confirmed"
    ]
    occupied = sum(int(b["party_size"]) for b in same_slot)
    if occupied + int(party_size) <= MAX_CAPACITY:
        return {"available": True, "alternatives": []}
    return {
        "available": False,
        "alternatives": [
            {"time": "19:30", "available": True},
            {"time": "20:45", "available": True},
            {"time": "21:15", "available": True}
        ]
    }

def create_booking_db(payload):
    booking = dict(payload)
    booking["booking_id"] = f"EB-{uuid.uuid4().hex[:8].upper()}"
    booking["status"] = "confirmed"
    booking["created_at"] = datetime.utcnow().isoformat()
    BOOKINGS.append(booking)
    return booking

def find_booking_db(name, phone_or_reference=None):
    for b in BOOKINGS:
        if b["name"].lower() == name.lower():
            if phone_or_reference is None:
                return b
            if b.get("phone") == phone_or_reference or b["booking_id"] == phone_or_reference:
                return b
    return None

def modify_booking_db(booking_id, updates):
    for b in BOOKINGS:
        if b["booking_id"] == booking_id:
            b.update(updates)
            b["updated_at"] = datetime.utcnow().isoformat()
            return {"success": True, "booking": b}
    return {"success": False, "message": "Booking not found"}

def cancel_booking_db(booking_id):
    for b in BOOKINGS:
        if b["booking_id"] == booking_id:
            b["status"] = "cancelled"
            b["updated_at"] = datetime.utcnow().isoformat()
            return {"success": True, "booking": b}
    return {"success": False, "message": "Booking not found"}

def create_order_db(payload):
    order = dict(payload)
    order["order_id"] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order["status"] = "requested"
    order["created_at"] = datetime.utcnow().isoformat()
    ORDERS.append(order)
    return order

def create_group_lead_db(payload):
    lead = dict(payload)
    lead["lead_id"] = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
    lead["status"] = "open"
    lead["created_at"] = datetime.utcnow().isoformat()
    LEADS.append(lead)
    return lead