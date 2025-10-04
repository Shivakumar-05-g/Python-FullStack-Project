#db_manager.py
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

# load environmental variables
load_dotenv()
url=os.getenv("SUPABASE_URL")
key=os.getenv("SUPABASE_KEY")

supabase=create_client(url, key)

class DatabaseManager:

	#create events
	def create_event(event_name, venue, date, total_seats, seats_available):
		return supabase.table("Events").insert({
			"event_name": event_name,
			"venue": venue,
			"date": date,
			"total_seats": total_seats,
			"seats_available": seats_available
		}).execute()

	#get all events
	def get_all_events():
		return supabase.table("Events").select("*").order("date").execute()

	#update events
	def update_event_seats(event_id, seats_available):
		return supabase.table("Events").update({
			"seats_available": seats_available
		}).eq("id", event_id).execute()

	#delete events
	def delete_event(event_id):
		return supabase.table("Events").delete().eq("id", event_id).execute()


	#create bookings
	def create_booking(user_name, user_email, event_id, seats_booked, booking_time=None):
		if booking_time is None:
			booking_time = datetime.isoformat()
		
		return supabase.table("Bookings").insert({
			"user_name": user_name,
			"user_email": user_email,
			"event_id": event_id,
			"seats_booked": seats_booked,
			"booking_time": booking_time
		}).execute()

	#get all bookings
	def get_all_bookings():
		return supabase.table("Bookings").select("*").execute()

	#update bookings
	def update_booking(booking_id, seats_booked):
		return supabase.table("Bookings").update({
			"seats_booked": seats_booked
		}).eq("id", booking_id).execute()

	#delete bookings
	def delete_booking(booking_id):
		return supabase.table("Bookings").delete().eq("id", booking_id).execute()