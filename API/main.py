from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel, EmailStr
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Ticket Booking System", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from src.logic import EventManager, BookingManager
    event_manager = EventManager()
    booking_manager = BookingManager()
except Exception as e:
    # Fall back to simple managers that use DatabaseManager directly.
    from src.db import DatabaseManager
    db = DatabaseManager()

    class EventManager:
        def add_event(self, event_name, venue, date, total_seats):
            result = db.create_event(event_name, venue, date, total_seats, total_seats)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                return {"success": True, "message": "Event created successfully", "data": data}
            return {"success": False, "message": str(error) if error else "Unknown error"}

        def get_events(self):
            result = db.get_all_events()
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data is not None:
                return {"success": True, "data": data}
            return {"success": False, "message": str(error) if error else "Unknown error"}

        def get_event(self, event_id):
            result = db.get_event_by_id(event_id)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                return {"success": True, "data": data}
            return {"success": False, "message": str(error) if error else "Event not found"}

        def delete_event(self, event_id):
            result = db.delete_event(event_id)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                return {"success": True, "message": "Event deleted successfully"}
            return {"success": False, "message": str(error) if error else "Unknown error"}

    class BookingManager:
        def book_event(self, user_name, user_email, event_id, seats_booked):
            result = db.create_booking(user_name, user_email, event_id, seats_booked)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                # decrement seats if possible
                ev = db.get_event_by_id(event_id)
                ev_data = getattr(ev, 'data', None)
                if ev_data and isinstance(ev_data, dict):
                    try:
                        avail = int(ev_data.get('seats_available', 0)) - int(seats_booked)
                        db.update_event_seats(event_id, avail)
                    except Exception:
                        pass
                return {"success": True, "message": "Booking created successfully", "data": data}
            return {"success": False, "message": str(error) if error else "Unknown error"}

        def get_all_bookings(self):
            result = db.get_all_bookings()
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data is not None:
                return {"success": True, "data": data}
            return {"success": False, "message": str(error) if error else "Unknown error"}

        def get_bookings_by_event(self, event_id):
            result = db.get_bookings_by_event(event_id)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data is not None:
                return {"success": True, "data": data}
            return {"success": False, "message": str(error) if error else "No bookings found"}

        def update_booking_seats(self, booking_id, seats_booked):
            result = db.update_booking(booking_id, seats_booked)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                return {"success": True, "message": "Booking updated successfully"}
            return {"success": False, "message": str(error) if error else "Unknown error"}

        def delete_booking(self, booking_id):
            result = db.delete_booking(booking_id)
            data = getattr(result, 'data', None)
            error = getattr(result, 'error', None)
            if data:
                return {"success": True, "message": "Booking deleted successfully"}
            return {"success": False, "message": str(error) if error else "Unknown error"}

    event_manager = EventManager()
    booking_manager = BookingManager()

# --- Models ---


class EventCreate(BaseModel):
    event_name: str
    venue: str
    date: str
    total_seats: int

class BookingCreate(BaseModel):
    user_name: str
    user_email: EmailStr
    event_id: int
    seats_booked: int

class BookingUpdate(BaseModel):
    seats_booked: int

# --- EVENTS ---
@app.get("/events")
def get_events():
    try:
        result = event_manager.get_events()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/events/{event_id}")
def get_event(event_id: int):
    try:
        result = event_manager.get_event(event_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/events")
def create_event(event: EventCreate):
    try:
        result = event_manager.add_event(event.event_name, event.venue, event.date, event.total_seats)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    try:
        result = event_manager.delete_event(event_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# --- BOOKINGS ---
@app.get("/bookings")
def get_all_bookings():
    try:
        result = booking_manager.get_all_bookings()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/bookings/event/{event_id}")
def get_bookings_by_event(event_id: int):
    try:
        result = booking_manager.get_bookings_by_event(event_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/bookings")
def create_booking(booking: BookingCreate):
    try:
        result = booking_manager.book_event(
            booking.user_name,
            booking.user_email,
            booking.event_id,
            booking.seats_booked,
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.put("/bookings/{booking_id}")
def update_booking(booking_id: int, update: BookingUpdate):
    try:
        result = booking_manager.update_booking_seats(booking_id, update.seats_booked)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    try:
        result = booking_manager.delete_booking(booking_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/")
def home():
    return {"message": "API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)