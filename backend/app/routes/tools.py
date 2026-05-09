import json
import uuid
import logging
from fastapi import APIRouter, Request, Response
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])


# ---------------------------------------------------------------------------
# Helper principal: extrai toolCallId e parâmetros do payload real do VAPI
#
# O VAPI envia sempre este formato:
# {
#   "message": {
#     "type": "tool-calls",
#     "toolCallList": [
#       {
#         "id": "call_abc123",
#         "type": "function",
#         "function": {
#           "name": "create_booking",
#           "arguments": "{\"restaurant_id\": \"elbarrio\", ...}"  <- string JSON
#         }
#       }
#     ]
#   }
# }
# ---------------------------------------------------------------------------
async def extract_tool_data(request: Request):
    body = await request.json()
    logger.debug("VAPI payload recebido: %s", json.dumps(body, indent=2))

    tool_call_id = None
    params = {}

    # --- Estrutura oficial do VAPI: message.toolCallList ---
    message = body.get("message", {})
    tool_call_list = message.get("toolCallList", [])

    if tool_call_list:
        first_call = tool_call_list[0]
        tool_call_id = first_call.get("id")
        raw_args = first_call.get("function", {}).get("arguments", "{}")
        # arguments chega como string JSON serializada — precisa de ser desserializada
        if isinstance(raw_args, str):
            try:
                params = json.loads(raw_args)
            except json.JSONDecodeError:
                logger.warning("Não foi possível fazer parse dos arguments: %s", raw_args)
                params = {}
        elif isinstance(raw_args, dict):
            params = raw_args
    else:
        # Fallback: alguns servidores/proxies aplanaram o payload
        tool_call_id = (
            body.get("toolCallId")
            or body.get("tool_call_id")
            or body.get("id")
        )
        # Tentar extrair parâmetros de vários locais possíveis
        params = (
            body.get("function", {}).get("arguments")
            or body.get("function", {}).get("parameters")
            or body.get("parameters")
            or body
        )
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                params = {}

    # Garantir que toolCallId nunca é None (VAPI rejeita respostas sem ele)
    if not tool_call_id:
        tool_call_id = f"fallback-{uuid.uuid4().hex[:8]}"
        logger.warning("toolCallId não encontrado no payload. Usando fallback: %s", tool_call_id)

    logger.debug("toolCallId extraído: %s", tool_call_id)
    logger.debug("parâmetros extraídos: %s", json.dumps(params, indent=2))
    return tool_call_id, params


def vapi_response(tool_call_id: str, result: dict) -> dict:
    """Formata a resposta no formato exato esperado pelo VAPI."""
    return {
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": json.dumps(result, ensure_ascii=False)
            }
        ]
    }


# ---------------------------------------------------------------------------
# Endpoints de ferramentas
# ---------------------------------------------------------------------------

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
    return vapi_response(tool_call_id, result)


@router.post("/create_booking")
async def tool_create_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_booking_called", params.get("restaurant_id"), params)
    track_metric("reservation_attempt", params.get("restaurant_id"), 1, {"channel": params.get("channel", "voice")})
    result = create_booking(params.get("restaurant_id"), params)
    if result.get("booking_id"):
        track_metric("reservation_created", params.get("restaurant_id"), 1, {"channel": params.get("channel")})
    log_event("create_booking_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/find_booking")
async def tool_find_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("find_booking_called", params.get("restaurant_id"), params)
    result = find_booking(
        params.get("restaurant_id"),
        params.get("name"),
        params.get("phone_or_reference")
    )
    log_event("find_booking_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/modify_booking")
async def tool_modify_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("modify_booking_called", params.get("restaurant_id"), params)
    result = modify_booking(
        params.get("restaurant_id"),
        params.get("booking_id"),
        params.get("updates")
    )
    if result.get("success"):
        track_metric("reservation_modified", params.get("restaurant_id"), 1)
    log_event("modify_booking_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/cancel_booking")
async def tool_cancel_booking(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("cancel_booking_called", params.get("restaurant_id"), params)
    result = cancel_booking(
        params.get("restaurant_id"),
        params.get("booking_id")
    )
    if result.get("success"):
        track_metric("reservation_cancelled", params.get("restaurant_id"), 1)
    log_event("cancel_booking_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/restaurant_kb")
async def tool_restaurant_kb(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("restaurant_kb_called", params.get("restaurant_id"), params)
    result = query_kb(params.get("restaurant_id"), params.get("query"))
    return vapi_response(tool_call_id, result)


@router.post("/get_seasonal_context")
async def tool_get_seasonal_context(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("seasonal_context_called", params.get("restaurant_id"), params)
    result = get_seasonal_context(params.get("restaurant_id"), params.get("date"))
    return vapi_response(tool_call_id, result)


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
    return vapi_response(tool_call_id, result)


@router.post("/suggest_order_slot")
async def tool_suggest_order_slot(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("suggest_order_slot_called", params.get("restaurant_id"), params)
    result = suggest_order_slot(
        params.get("restaurant_id"),
        params.get("requested_time"),
        params.get("kitchen_status")
    )
    return vapi_response(tool_call_id, result)


@router.post("/create_order_request")
async def tool_create_order_request(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_order_request_called", params.get("restaurant_id"), params)
    track_metric("order_attempt", params.get("restaurant_id"), 1, {"channel": params.get("channel", "voice")})
    result = create_order_request(params)
    if result.get("order_id"):
        track_metric("order_created", params.get("restaurant_id"), 1, {"channel": params.get("channel")})
    log_event("create_order_request_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/create_group_lead")
async def tool_create_group_lead(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("create_group_lead_called", params.get("restaurant_id"), params)
    result = create_group_lead(params)
    if result.get("lead_id"):
        track_metric("group_lead_created", params.get("restaurant_id"), 1)
    log_event("create_group_lead_result", params.get("restaurant_id"), result)
    return vapi_response(tool_call_id, result)


@router.post("/handoff_to_staff")
async def tool_handoff_to_staff(request: Request):
    tool_call_id, params = await extract_tool_data(request)
    log_event("handoff_to_staff_called", params.get("restaurant_id"), params)
    result = handoff_to_staff(params.get("restaurant_id"), params.get("reason"))
    track_metric("handoff_triggered", params.get("restaurant_id"), 1, {"reason": params.get("reason")})
    return vapi_response(tool_call_id, result)
