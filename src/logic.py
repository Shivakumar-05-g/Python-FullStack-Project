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
