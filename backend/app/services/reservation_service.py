from app.config import USE_PROVIDER
from app.services.fallback_db import (
    check_availability_db,
    create_booking_db,
    find_booking_db,
    modify_booking_db,
    cancel_booking_db
)
from app.services.sheets_service import (
    check_availability_sheets,
    create_booking_sheets,
    find_booking_sheets
)
from app.services.zenchef_adapter import ZenchefAdapter

zenchef = ZenchefAdapter()

def check_availability(restaurant_id, date, time, party_size, seating_preference=None):
    if USE_PROVIDER == "zenchef":
        result = zenchef.check_availability(restaurant_id, date, time, party_size, seating_preference)
        if result.get("available") is not None:
            return result
    elif USE_PROVIDER == "sheets":
        return check_availability_sheets(date, time, party_size)
    return check_availability_db(date, time, party_size)

def create_booking(restaurant_id, payload):
    if USE_PROVIDER == "zenchef":
        result = zenchef.create_booking(restaurant_id, payload)
        if result.get("success"):
            return result
    elif USE_PROVIDER == "sheets":
        return create_booking_sheets(payload)
    return create_booking_db(payload)

def find_booking(restaurant_id, name, phone_or_reference=None):
    if USE_PROVIDER == "zenchef":
        result = zenchef.find_booking(restaurant_id, name, phone_or_reference)
        if result:
            return result
    elif USE_PROVIDER == "sheets":
        return find_booking_sheets(name, phone_or_reference)
    return find_booking_db(name, phone_or_reference)

def modify_booking(restaurant_id, booking_id, updates):
    return modify_booking_db(booking_id, updates)

def cancel_booking(restaurant_id, booking_id):
    return cancel_booking_db(booking_id)