from src.db import DatabaseManager


# small helper to normalize Supabase/in-memory response shapes
def _extract_data(result):
    """
    Given a DB result object (may have .data which is a dict, list, or None),
    return a normalized Python object: a dict for single-record responses or
    a list for multi-record responses.
    """
    data = getattr(result, "data", None)
    if data is None:
        return None
    # If supabase returns a single dict via .data (when using .single()), keep it
    if isinstance(data, dict):
        return data
    # If data is a list with one element, and caller expects a single record, return that dict
    if isinstance(data, list) and len(data) == 1:
        return data[0]
    return data


class EventManager:
    def __init__(self):
        self.db = DatabaseManager()

    def add_event(self, event_name, venue, date, total_seats):
        '''
        Add a new event.
        seats_available is initially set equal to total_seats.
        '''
        if not event_name or not venue or not date or total_seats <= 0:
            return {"success": False, "message": "Invalid event data: all fields required and seats must be > 0"}

        seats_available = total_seats
        result = self.db.create_event(event_name, venue, date, total_seats, seats_available)
        data = _extract_data(result)
        error = getattr(result, "error", None)
        if data is not None:
            return {"success": True, "message": "Event created successfully", "data": data}
        error_msg = str(error) if error else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    def get_events(self):
        '''
        Get all events
        '''
        result = self.db.get_all_events()
        data = _extract_data(result)
        error = getattr(result, "error", None)
        if data is not None:
            return {"success": True, "data": data}
        error_msg = str(error) if error else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    def get_event(self, event_id):
        '''
        Get a single event by ID
        '''
        result = self.db.get_event_by_id(event_id)
        data = _extract_data(result)
        error = getattr(result, "error", None)
        if data is not None:
            return {"success": True, "data": data}
        error_msg = str(error) if error else "Event not found"
        return {"success": False, "message": f"Error: {error_msg}"}

    def delete_event(self, event_id):
        '''
        Delete an event
        '''
        result = self.db.delete_event(event_id)
        data = _extract_data(result)
        if data is not None:
            return {"success": True, "message": "Event deleted successfully"}
        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    # ======================
    # BOOKINGS
    # ======================
class BookingManager:
    def __init__(self):
        self.db = DatabaseManager()

    def book_event(self, user_name, user_email, event_id, seats_booked):
        """
        Create a new booking for an event
        """
        # stricter validation: event_id may be 0 if invalid; check for None
        if not user_name or not user_email or event_id is None or seats_booked <= 0:
            return {"success": False, "message": "Invalid booking data"}

        # Check event exists and has enough seats
        ev_result = self.db.get_event_by_id(event_id)
        ev_data = _extract_data(ev_result)
        if not ev_data:
            return {"success": False, "message": "Event not found"}

        # ev_data should be a dict representing the event
        seats_available = ev_data.get("seats_available") if isinstance(ev_data, dict) else None
        try:
            seats_available = int(seats_available) if seats_available is not None else None
        except Exception:
            seats_available = None

        if seats_available is not None and seats_booked > seats_available:
            return {"success": False, "message": "Not enough seats available"}

        result = self.db.create_booking(user_name, user_email, event_id, seats_booked)
        res_data = _extract_data(result)
        # If booking succeeded, decrement seats_available
        if res_data is not None:
            if seats_available is not None:
                new_available = seats_available - seats_booked
                try:
                    self.db.update_event_seats(event_id, new_available)
                except Exception:
                    # non-fatal: booking succeeded but seat update failed
                    pass
            return {"success": True, "message": "Booking created successfully", "data": res_data}

        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    def get_all_bookings(self):
        '''
        Get all bookings
        '''
        result = self.db.get_all_bookings()
        data = _extract_data(result)
        if data is not None:
            return {"success": True, "data": data}
        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    def get_bookings_by_event(self, event_id):
        '''
        Get all bookings for a specific event
        '''
        result = self.db.get_bookings_by_event(event_id)
        data = _extract_data(result)
        if data is not None:
            return {"success": True, "data": data}
        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "No bookings found"
        return {"success": False, "message": f"Error: {error_msg}"}

    def update_booking_seats(self, booking_id, seats_booked):
        '''
        Update the number of seats in an existing booking
        '''
        if seats_booked <= 0:
            return {"success": False, "message": "Seats booked must be greater than 0"}

        result = self.db.update_booking(booking_id, seats_booked)
        data = _extract_data(result)
        if data is not None:
            return {"success": True, "message": "Booking updated successfully"}
        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}

    def delete_booking(self, booking_id):
        '''
        Cancel/delete a booking
        '''
        result = self.db.delete_booking(booking_id)
        data = _extract_data(result)
        if data is not None:
            return {"success": True, "message": "Booking deleted successfully"}
        error_msg = str(getattr(result, 'error', None)) if getattr(result, 'error', None) else "Unknown error"
        return {"success": False, "message": f"Error: {error_msg}"}