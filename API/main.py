from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Mock database
users = {}
events = {
	1: {
		"name": "Concert A",
		"seats": {str(i): None for i in range(1, 51)}  # 50 seats
	}
}
bookings = []

# Models
class User(BaseModel):
	username: str
	password: str
	is_admin: bool = False

class LoginRequest(BaseModel):
	username: str
	password: str

class RegisterRequest(BaseModel):
	username: str
	password: str

class PaymentRequest(BaseModel):
	username: str
	event_id: int
	seat: str
	amount: float

class Booking(BaseModel):
	username: str
	event_id: int
	seat: str

# Authentication endpoints
@app.post("/register")
def register(req: RegisterRequest):
	if req.username in users:
		raise HTTPException(status_code=400, detail="User already exists")
	users[req.username] = {"password": req.password, "is_admin": False}
	return {"message": "Registered successfully"}

@app.post("/login")
def login(req: LoginRequest):
	user = users.get(req.username)
	if not user or user["password"] != req.password:
		raise HTTPException(status_code=401, detail="Invalid credentials")
	return {"message": "Login successful", "is_admin": user["is_admin"]}

# Seat selection
@app.get("/events/{event_id}/seats")
def get_seats(event_id: int):
	event = events.get(event_id)
	if not event:
		raise HTTPException(status_code=404, detail="Event not found")
	return event["seats"]

# Payment (mock)
@app.post("/pay")
def pay(req: PaymentRequest):
	event = events.get(req.event_id)
	if not event:
		raise HTTPException(status_code=404, detail="Event not found")
	if event["seats"][req.seat] is not None:
		raise HTTPException(status_code=400, detail="Seat already booked")
	# Mock payment success
	event["seats"][req.seat] = req.username
	bookings.append({"username": req.username, "event_id": req.event_id, "seat": req.seat})
	return {"message": "Payment successful, seat booked"}

# Admin dashboard
@app.get("/admin/bookings")
def get_bookings(username: str):
	user = users.get(username)
	if not user or not user["is_admin"]:
		raise HTTPException(status_code=403, detail="Admin access required")
	return bookings

@app.post("/admin/events")
def add_event(username: str, name: str, seat_count: int):
	user = users.get(username)
	if not user or not user["is_admin"]:
		raise HTTPException(status_code=403, detail="Admin access required")
	event_id = max(events.keys()) + 1
	events[event_id] = {"name": name, "seats": {str(i): None for i in range(1, seat_count + 1)}}
	return {"message": "Event added", "event_id": event_id}
