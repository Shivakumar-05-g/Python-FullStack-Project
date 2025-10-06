from src.db import DatabaseManager

    # ======================
    # EVENTS
    # ======================
class EventManager:
    def __init__(self):
        self.db = DatabaseManager

    def add_event(self, event_name, venue, date, total_seats):
        '''
        Add a new event.
        seats_available is initially set equal to total_seats.
        '''
        if not event_name or not venue or not date or total_seats <= 0:
            return {"success": False, "message": "Invalid event data: all fields required and seats must be > 0"}

        seats_available = total_seats
        result = self.db.create_event(event_name, venue, date, total_seats, seats_available)

        if result.data:
            return {"success": True, "message": "Event created successfully"}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    def get_events(self):
        '''
        Get all events
        '''
        result = self.db.get_all_events()
        if result.data is not None:
            return {"success": True, "data": result.data}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    def get_event(self, event_id):
        '''
        Get a single event by ID
        '''
        result = self.db.get_event_by_id(event_id)
        if result.data:
            return {"success": True, "data": result.data}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Event not found"
            return {"success": False, "message": f"Error: {error_msg}"}

    def delete_event(self, event_id):
        '''
        Delete an event
        '''
        result = self.db.delete_event(event_id)
        if result.data:
            return {"success": True, "message": "Event deleted successfully"}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    # ======================
    # BOOKINGS
    # ======================
class BookingManager:
    def __init__(self):
        self.db = DatabaseManager

    def book_event(self, user_name, user_email, event_id, seats_booked):
        '''
        Create a new booking for an event
        '''
        if not user_name or not user_email or not event_id or seats_booked <= 0:
            return {"success": False, "message": "Invalid booking data"}

        # Optional: Check if event exists and has enough seats (you can add this later)
        result = self.db.create_booking(user_name, user_email, event_id, seats_booked)

        if result.data:
            return {"success": True, "message": "Booking created successfully"}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    def get_all_bookings(self):
        '''
        Get all bookings
        '''
        result = self.db.get_all_bookings()
        if result.data is not None:
            return {"success": True, "data": result.data}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    def get_bookings_by_event(self, event_id):
        '''
        Get all bookings for a specific event
        '''
        result = self.db.get_bookings_by_event(event_id)
        if result.data is not None:
            return {"success": True, "data": result.data}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "No bookings found"
            return {"success": False, "message": f"Error: {error_msg}"}

    def update_booking_seats(self, booking_id, seats_booked):
        '''
        Update the number of seats in an existing booking
        '''
        if seats_booked <= 0:
            return {"success": False, "message": "Seats booked must be greater than 0"}

        result = self.db.update_booking(booking_id, seats_booked)
        if result.data:
            return {"success": True, "message": "Booking updated successfully"}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}

    def delete_booking(self, booking_id):
        '''
        Cancel/delete a booking
        '''
        result = self.db.delete_booking(booking_id)
        if result.data:
            return {"success": True, "message": "Booking deleted successfully"}
        else:
            error_msg = str(result.error) if hasattr(result, 'error') else "Unknown error"
            return {"success": False, "message": f"Error: {error_msg}"}












































'''
# Business logic functions
from src.db import users, events, bookings

def register_user(username, password):
	if username in users:
		return False, "User already exists"
	users[username] = {"password": password, "is_admin": False}
	return True, "Registered successfully"

def login_user(username, password):
	user = users.get(username)
	if not user or user["password"] != password:
		return False, "Invalid credentials"
	return True, user["is_admin"]

def get_event_seats(event_id):
	event = events.get(event_id)
	if not event:
		return None
	return event["seats"]

def book_seat(username, event_id, seat):
	event = events.get(event_id)
	if not event:
		return False, "Event not found"
	if event["seats"][seat] is not None:
		return False, "Seat already booked"
	event["seats"][seat] = username
	bookings.append({"username": username, "event_id": event_id, "seat": seat})
	return True, "Seat booked"

def add_event(username, name, seat_count):
	user = users.get(username)
	if not user or not user["is_admin"]:
		return False, "Admin access required"
	event_id = max(events.keys()) + 1
	events[event_id] = {"name": name, "seats": {str(i): None for i in range(1, seat_count + 1)}}
	return True, event_id
'''