# db_manager.py
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
from types import SimpleNamespace

# load environmental variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Try to create a Supabase client; if it fails, we'll fall back to an in-memory store
supabase = None
if url and key:
	try:
		supabase = create_client(url, key)
	except Exception:
		supabase = None

# Helpful startup message for debugging
if supabase is None:
    print("[DatabaseManager] Supabase client not initialized — using in-memory fallback.")
else:
    print("[DatabaseManager] Supabase client initialized.")


class DatabaseManager:
	"""Wrapper around Supabase client for Events and Bookings tables.

	If Supabase isn't configured or cannot be reached, this class falls back to
	a simple in-memory store so the API can run for local testing.
	"""

	def __init__(self):
		self.client = supabase
		self.use_memory = self.client is None
		if self.use_memory:
			# in-memory stores
			self.events = []
			self.bookings = []
			self._next_event_id = 1
			self._next_booking_id = 1

	# create events
	def create_event(self, event_name, venue, date, total_seats, seats_available):
		if self.use_memory:
			ev = {
				"id": self._next_event_id,
				"event_name": event_name,
				"venue": venue,
				"date": date,
				"total_seats": total_seats,
				"seats_available": seats_available,
			}
			self.events.append(ev)
			self._next_event_id += 1
			return SimpleNamespace(data=[ev], error=None)
		return self.client.table("events").insert({
			"event_name": event_name,
			"venue": venue,
			"date": date,
			"total_seats": total_seats,
			"seats_available": seats_available,
		}).execute()

	# get all events
	def get_all_events(self):
		if self.use_memory:
			# return a list under .data to match supabase response shape
			return SimpleNamespace(data=self.events.copy(), error=None)
		return self.client.table("events").select("*").order("date").execute()

	# get single event by id
	def get_event_by_id(self, event_id):
		if self.use_memory:
			for ev in self.events:
				if int(ev.get("id")) == int(event_id):
					return SimpleNamespace(data=ev, error=None)
			return SimpleNamespace(data=None, error="Not found")
		return self.client.table("events").select("*").eq("id", event_id).single().execute()

	# update events
	def update_event_seats(self, event_id, seats_available):
		if self.use_memory:
			for ev in self.events:
				if int(ev.get("id")) == int(event_id):
					ev["seats_available"] = seats_available
					return SimpleNamespace(data=[ev], error=None)
			return SimpleNamespace(data=None, error="Not found")
		return self.client.table("events").update({
			"seats_available": seats_available
		}).eq("id", event_id).execute()

	# delete events
	def delete_event(self, event_id):
		if self.use_memory:
			for i, ev in enumerate(self.events):
				if int(ev.get("id")) == int(event_id):
					removed = self.events.pop(i)
					return SimpleNamespace(data=[removed], error=None)
			return SimpleNamespace(data=None, error="Not found")
		return self.client.table("events").delete().eq("id", event_id).execute()

	# create bookings
	def create_booking(self, user_name, user_email, event_id, seats_booked, booking_time=None):
		if booking_time is None:
			booking_time = datetime.now().isoformat()
		if self.use_memory:
			bk = {
				"id": self._next_booking_id,
				"user_name": user_name,
				"user_email": user_email,
				"event_id": int(event_id),
				"seats_booked": int(seats_booked),
				"booking_time": booking_time,
			}
			self.bookings.append(bk)
			self._next_booking_id += 1
			return SimpleNamespace(data=[bk], error=None)
		return self.client.table("bookings").insert({
			"user_name": user_name,
			"user_email": user_email,
			"event_id": event_id,
			"seats_booked": seats_booked,
			"booking_time": booking_time,
		}).execute()

	# get all bookings
	def get_all_bookings(self):
		if self.use_memory:
			return SimpleNamespace(data=self.bookings.copy(), error=None)
		return self.client.table("bookings").select("*").execute()

	# get bookings by event
	def get_bookings_by_event(self, event_id):
		if self.use_memory:
			data = [b for b in self.bookings if int(b.get("event_id")) == int(event_id)]
			return SimpleNamespace(data=data, error=None)
		return self.client.table("bookings").select("*").eq("event_id", event_id).execute()

	# update bookings
	def update_booking(self, booking_id, seats_booked):
		if self.use_memory:
			for b in self.bookings:
				if int(b.get("id")) == int(booking_id):
					b["seats_booked"] = int(seats_booked)
					return SimpleNamespace(data=[b], error=None)
			return SimpleNamespace(data=None, error="Not found")
		return self.client.table("bookings").update({
			"seats_booked": seats_booked
		}).eq("id", booking_id).execute()

	# delete bookings
	def delete_booking(self, booking_id):
		if self.use_memory:
			for i, b in enumerate(self.bookings):
				if int(b.get("id")) == int(booking_id):
					removed = self.bookings.pop(i)
					return SimpleNamespace(data=[removed], error=None)
			return SimpleNamespace(data=None, error="Not found")
		return self.client.table("bookings").delete().eq("id", booking_id).execute()
