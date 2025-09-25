from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from pydantic import BaseModel, EmailStr
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logic import TaskManager, EventManager, BookingManager

app = FastAPI(title="Student Task & Event Manager", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_manager = TaskManager()
event_manager = EventManager()
booking_manager = BookingManager()  

# --- Models ---
class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: str
    priority: str

class TaskUpdate(BaseModel):
    completed: bool

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

# --- TASKS ---
@app.get("/tasks")
def get_tasks():
    result = task_manager.get_tasks()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/tasks")
def create_task(task: TaskCreate):
    result = task_manager.add_task(task.title, task.description, task.due_date, task.priority)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.put("/tasks/{task_id}") 
def update_task(task_id: int, task: TaskUpdate):
    if task.completed:
        result = task_manager.mark_complete(task_id)
    else:
        result = task_manager.mark_pending(task_id) 
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.delete("/tasks/{task_id}") 
def delete_task(task_id: int):
    result = task_manager.delete_task(task_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- EVENTS ---
@app.get("/events")
def get_events():
    result = event_manager.get_events()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.get("/events/{event_id}")
def get_event(event_id: int):
    result = event_manager.get_event(event_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/events")
def create_event(event: EventCreate):
    result = event_manager.add_event(event.event_name, event.venue, event.date, event.total_seats)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    result = event_manager.delete_event(event_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- BOOKINGS ---
@app.get("/bookings")
def get_all_bookings():
    result = booking_manager.get_all_bookings()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.get("/bookings/event/{event_id}")
def get_bookings_by_event(event_id: int):
    result = booking_manager.get_bookings_by_event(event_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.post("/bookings")
def create_booking(booking: BookingCreate):
    result = booking_manager.book_event(
        booking.user_name,
        booking.user_email,
        booking.event_id,
        booking.seats_booked
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.put("/bookings/{booking_id}")
def update_booking(booking_id: int, update: BookingUpdate):
    result = booking_manager.update_booking_seats(booking_id, update.seats_booked)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    result = booking_manager.delete_booking(booking_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/")
def home():
    return {"message": "API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)