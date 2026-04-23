class ZenchefAdapter:
    def __init__(self):
        pass

    def check_availability(self, restaurant_id, date, time, party_size, seating_preference=None):
        return {"available": None, "provider": "zenchef", "message": "Zenchef adapter not yet configured"}

    def create_booking(self, restaurant_id, payload):
        return {"success": False, "provider": "zenchef", "message": "Zenchef adapter not yet configured"}

    def find_booking(self, restaurant_id, name, phone_or_reference=None):
        return None

    def modify_booking(self, restaurant_id, booking_id, updates):
        return {"success": False, "provider": "zenchef", "message": "Zenchef adapter not yet configured"}

    def cancel_booking(self, restaurant_id, booking_id):
        return {"success": False, "provider": "zenchef", "message": "Zenchef adapter not yet configured"}