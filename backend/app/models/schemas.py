from pydantic import BaseModel
from typing import Optional, Dict, Any

class AvailabilityRequest(BaseModel):
    restaurant_id: str
    date: str
    time: str
    party_size: int
    seating_preference: Optional[str] = None

class CreateBookingRequest(BaseModel):
    restaurant_id: str
    name: str
    phone: Optional[str] = None
    date: str
    time: str
    party_size: int
    seating_preference: Optional[str] = None
    occasion: Optional[str] = None
    notes: Optional[str] = None
    language: Optional[str] = None
    channel: Optional[str] = "voice"

class FindBookingRequest(BaseModel):
    restaurant_id: str
    name: str
    phone_or_reference: Optional[str] = None

class ModifyBookingRequest(BaseModel):
    restaurant_id: str
    booking_id: str
    updates: Dict[str, Any]

class CancelBookingRequest(BaseModel):
    restaurant_id: str
    booking_id: str

class KBQueryRequest(BaseModel):
    restaurant_id: str
    query: str

class SeasonalContextRequest(BaseModel):
    restaurant_id: str
    date: str

class KitchenLoadRequest(BaseModel):
    restaurant_id: str
    date: str
    time: str
    order_type: str
    estimated_size: Optional[str] = None

class OrderSlotSuggestionRequest(BaseModel):
    restaurant_id: str
    requested_time: str
    kitchen_status: str

class CreateOrderRequest(BaseModel):
    restaurant_id: str
    name: str
    phone: Optional[str] = None
    date: str
    requested_time: str
    order_type: str
    items: Optional[str] = None
    notes: Optional[str] = None
    language: Optional[str] = None
    channel: Optional[str] = "voice"

class GroupLeadRequest(BaseModel):
    restaurant_id: str
    contact_name: str
    phone: Optional[str] = None
    date: str
    guest_count: int
    event_type: str
    notes: Optional[str] = None

class HandoffRequest(BaseModel):
    restaurant_id: str
    reason: str