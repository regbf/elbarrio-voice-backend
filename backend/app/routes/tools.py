from fastapi import APIRouter
from app.models.schemas import *
from app.services.reservation_service import (
    check_availability,
    create_booking,
    find_booking,
    modify_booking,
    cancel_booking
)
from app.services.kb_service import query_kb
from app.services.seasonal_service import get_seasonal_context
from app.services.kitchen_service import check_kitchen_load, suggest_order_slot
from app.services.lead_service import create_group_lead, create_order_request, handoff_to_staff
from app.services.logging_service import log_event
from app.services.analytics_service import track_metric

router = APIRouter(prefix="/tools", tags=["tools"])

@router.post("/check_availability")
def tool_check_availability(req: AvailabilityRequest):
    log_event("check_availability_called", req.restaurant_id, req.dict())
    track_metric("reservation_availability_check", req.restaurant_id, 1, {"channel": "voice"})
    result = check_availability(req.restaurant_id, req.date, req.time, req.party_size, req.seating_preference)
    log_event("check_availability_result", req.restaurant_id, result)
    return result

@router.post("/create_booking")
def tool_create_booking(req: CreateBookingRequest):
    log_event("create_booking_called", req.restaurant_id, req.dict())
    track_metric("reservation_attempt", req.restaurant_id, 1, {"channel": req.channel})
    result = create_booking(req.restaurant_id, req.dict())
    if result.get("booking_id"):
        track_metric("reservation_created", req.restaurant_id, 1, {"channel": req.channel})
    log_event("create_booking_result", req.restaurant_id, result)
    return result

@router.post("/find_booking")
def tool_find_booking(req: FindBookingRequest):
    log_event("find_booking_called", req.restaurant_id, req.dict())
    result = find_booking(req.restaurant_id, req.name, req.phone_or_reference)
    log_event("find_booking_result", req.restaurant_id, result)
    return result

@router.post("/modify_booking")
def tool_modify_booking(req: ModifyBookingRequest):
    log_event("modify_booking_called", req.restaurant_id, req.dict())
    result = modify_booking(req.restaurant_id, req.booking_id, req.updates)
    if result.get("success"):
        track_metric("reservation_modified", req.restaurant_id, 1)
    log_event("modify_booking_result", req.restaurant_id, result)
    return result

@router.post("/cancel_booking")
def tool_cancel_booking(req: CancelBookingRequest):
    log_event("cancel_booking_called", req.restaurant_id, req.dict())
    result = cancel_booking(req.restaurant_id, req.booking_id)
    if result.get("success"):
        track_metric("reservation_cancelled", req.restaurant_id, 1)
    log_event("cancel_booking_result", req.restaurant_id, result)
    return result

@router.post("/restaurant_kb")
def tool_restaurant_kb(req: KBQueryRequest):
    log_event("restaurant_kb_called", req.restaurant_id, req.dict())
    result = query_kb(req.restaurant_id, req.query)
    return result

@router.post("/get_seasonal_context")
def tool_get_seasonal_context(req: SeasonalContextRequest):
    log_event("seasonal_context_called", req.restaurant_id, req.dict())
    result = get_seasonal_context(req.restaurant_id, req.date)
    return result

@router.post("/check_kitchen_load")
def tool_check_kitchen_load(req: KitchenLoadRequest):
    log_event("check_kitchen_load_called", req.restaurant_id, req.dict())
    result = check_kitchen_load(req.restaurant_id, req.date, req.time, req.order_type, req.estimated_size)
    if result.get("status") == "busy":
        track_metric("kitchen_busy_detected", req.restaurant_id, 1, {"time": req.time})
    if result.get("status") == "overloaded":
        track_metric("kitchen_overloaded_detected", req.restaurant_id, 1, {"time": req.time})
    log_event("check_kitchen_load_result", req.restaurant_id, result)
    return result

@router.post("/suggest_order_slot")
def tool_suggest_order_slot(req: OrderSlotSuggestionRequest):
    log_event("suggest_order_slot_called", req.restaurant_id, req.dict())
    result = suggest_order_slot(req.restaurant_id, req.requested_time, req.kitchen_status)
    return result

@router.post("/create_order_request")
def tool_create_order_request(req: CreateOrderRequest):
    log_event("create_order_request_called", req.restaurant_id, req.dict())
    track_metric("order_attempt", req.restaurant_id, 1, {"channel": req.channel})
    result = create_order_request(req.dict())
    if result.get("order_id"):
        track_metric("order_created", req.restaurant_id, 1, {"channel": req.channel})
    log_event("create_order_request_result", req.restaurant_id, result)
    return result

@router.post("/create_group_lead")
def tool_create_group_lead(req: GroupLeadRequest):
    log_event("create_group_lead_called", req.restaurant_id, req.dict())
    result = create_group_lead(req.dict())
    if result.get("lead_id"):
        track_metric("group_lead_created", req.restaurant_id, 1)
    log_event("create_group_lead_result", req.restaurant_id, result)
    return result

@router.post("/handoff_to_staff")
def tool_handoff_to_staff(req: HandoffRequest):
    log_event("handoff_to_staff_called", req.restaurant_id, req.dict())
    result = handoff_to_staff(req.restaurant_id, req.reason)
    track_metric("handoff_triggered", req.restaurant_id, 1, {"reason": req.reason})
    return result