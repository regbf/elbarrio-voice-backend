import json
from fastapi import APIRouter, Request, Response
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

# ---------- Helper para extrair toolCallId e parâmetros ----------
async def extract_tool_data(request: Request):
    body = await request.json()
    tool_call_id = body.get("toolCallId")
    # Alguns casos: Vapi envia dentro de 'function'
    params = body.get("function", {}).get("parameters", body)
    return tool_call_id, params

# ---------- Preflight HEAD/GET para todas as rotas ----------
def add_preflight(endpoint: str):
    @router.head(endpoint)
    @router.get(endpoint)
    async def preflight():
        return Response(status_code=200, content="OK")

# Lista de todos os endpoints
endpoints = [
    "check_availability", "create_booking", "find_booking",
    "modify_booking", "cancel_booking", "restaurant_kb",
    "get_seasonal_context", "check_kitchen_load", "suggest_order_slot",
    "create_order_request", "create_group_lead", "handoff_to_staff"
]
for ep in endpoints:
    add_preflight(ep)

# ---------- Ferramentas com resposta no formato Vapi ----------
@router.post("/check_availability")
async def tool_check_availability(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    result = check_availability(
        params.get("restaurant_id"),
        params.get("date"),
        params.get("time"),
        params.get("party_size"),
        params.get("seating_preference")
    )
    log_event("check_availability_called", params.get("restaurant_id"), params)
    track_metric("reservation_availability_check", params.get("restaurant_id"), 1, {"channel": "voice"})
    log_event("check_availability_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/create_booking")
async def tool_create_booking(request: Request):
    # Log do pedido completo
    print("=== REQUEST RECEIVED ===")
    print("Headers:", dict(request.headers))
    body = await request.json()
    print("Body:", json.dumps(body, indent=2))
    
    tool_call_id = body.get("toolCallId")
    if not tool_call_id:
        tool_call_id = "fallback-" + str(uuid.uuid4())
        print("WARNING: toolCallId not provided, using", tool_call_id)
    
    params = body.get("function", {}).get("parameters", body)
    # ... resto do código ...
    
    result = create_booking(...)
    
    response_data = {
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": json.dumps(result)
            }
        ]
    }
    print("=== RESPONSE SENT ===")
    print(json.dumps(response_data, indent=2))
    return response_data

@router.head("/create_booking")
@router.get("/create_booking")
async def create_booking_preflight():
    return Response(status_code=200, content="OK")

@router.post("/create_booking")
async def tool_create_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_booking_called", params.get("restaurant_id"), params)
    track_metric("reservation_attempt", params.get("restaurant_id"), 1, {"channel": params.get("channel", "voice")})
    result = create_booking(params.get("restaurant_id"), params)
    if result.get("booking_id"):
        track_metric("reservation_created", params.get("restaurant_id"), 1, {"channel": params.get("channel")})
    log_event("create_booking_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/find_booking")
async def tool_find_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("find_booking_called", params.get("restaurant_id"), params)
    result = find_booking(params.get("restaurant_id"), params.get("name"), params.get("phone_or_reference"))
    log_event("find_booking_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/modify_booking")
async def tool_modify_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("modify_booking_called", params.get("restaurant_id"), params)
    result = modify_booking(params.get("restaurant_id"), params.get("booking_id"), params.get("updates"))
    if result.get("success"):
        track_metric("reservation_modified", params.get("restaurant_id"), 1)
    log_event("modify_booking_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/cancel_booking")
async def tool_cancel_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("cancel_booking_called", params.get("restaurant_id"), params)
    result = cancel_booking(params.get("restaurant_id"), params.get("booking_id"))
    if result.get("success"):
        track_metric("reservation_cancelled", params.get("restaurant_id"), 1)
    log_event("cancel_booking_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/restaurant_kb")
async def tool_restaurant_kb(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("restaurant_kb_called", params.get("restaurant_id"), params)
    result = query_kb(params.get("restaurant_id"), params.get("query"))
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/get_seasonal_context")
async def tool_get_seasonal_context(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("seasonal_context_called", params.get("restaurant_id"), params)
    result = get_seasonal_context(params.get("restaurant_id"), params.get("date"))
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/check_kitchen_load")
async def tool_check_kitchen_load(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("check_kitchen_load_called", params.get("restaurant_id"), params)
    result = check_kitchen_load(
        params.get("restaurant_id"),
        params.get("date"),
        params.get("time"),
        params.get("order_type"),
        params.get("estimated_size")
    )
    if result.get("status") == "busy":
        track_metric("kitchen_busy_detected", params.get("restaurant_id"), 1, {"time": params.get("time")})
    if result.get("status") == "overloaded":
        track_metric("kitchen_overloaded_detected", params.get("restaurant_id"), 1, {"time": params.get("time")})
    log_event("check_kitchen_load_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/suggest_order_slot")
async def tool_suggest_order_slot(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("suggest_order_slot_called", params.get("restaurant_id"), params)
    result = suggest_order_slot(
        params.get("restaurant_id"),
        params.get("requested_time"),
        params.get("kitchen_status")
    )
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/create_order_request")
async def tool_create_order_request(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_order_request_called", params.get("restaurant_id"), params)
    track_metric("order_attempt", params.get("restaurant_id"), 1, {"channel": params.get("channel", "voice")})
    result = create_order_request(params)
    if result.get("order_id"):
        track_metric("order_created", params.get("restaurant_id"), 1, {"channel": params.get("channel")})
    log_event("create_order_request_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/create_group_lead")
async def tool_create_group_lead(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_group_lead_called", params.get("restaurant_id"), params)
    result = create_group_lead(params)
    if result.get("lead_id"):
        track_metric("group_lead_created", params.get("restaurant_id"), 1)
    log_event("create_group_lead_result", params.get("restaurant_id"), result)
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}

@router.post("/handoff_to_staff")
async def tool_handoff_to_staff(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("handoff_to_staff_called", params.get("restaurant_id"), params)
    result = handoff_to_staff(params.get("restaurant_id"), params.get("reason"))
    track_metric("handoff_triggered", params.get("restaurant_id"), 1, {"reason": params.get("reason")})
    return {"results": [{"toolCallId": tool_call_id, "result": json.dumps(result)}]}
