def check_kitchen_load(restaurant_id, date, time, order_type, estimated_size=None):
    # Simulação simples baseada na hora
    if time in ["19:30", "20:00", "20:30"]:
        return {"status": "busy"}
    if time in ["21:00"]:
        return {"status": "overloaded"}
    return {"status": "normal"}

def suggest_order_slot(restaurant_id, requested_time, kitchen_status):
    if kitchen_status == "busy":
        return {"alternatives": ["20:20", "20:35"]}
    if kitchen_status == "overloaded":
        return {"alternatives": ["21:20", "21:40", "22:00"]}
    return {"alternatives": [requested_time]}