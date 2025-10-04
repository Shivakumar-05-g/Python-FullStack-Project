import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Student Task & Event Manager", layout="centered")

def show_events():
    st.header("Available Events")
    resp = requests.get(f"{API_URL}/events")
    if resp.status_code == 200:
        events = resp.json().get("data", [])
        for event in events:
            st.subheader(event["event_name"])
            st.write(f"Venue: {event['venue']}")
            st.write(f"Date: {event['date']}")
            st.write(f"Total Seats: {event['total_seats']}")
            st.write(f"Seats Available: {event['seats_available']}")
            if st.button(f"Book for {event['event_name']}", key=f"book_{event['id']}"):
                st.session_state["selected_event"] = event
                st.session_state["page"] = "book"
    else:
        st.error("Could not fetch events.")

def create_event():
    st.header("Create New Event (Admin)")
    event_name = st.text_input("Event Name")
    venue = st.text_input("Venue")
    date = st.date_input("Date")
    total_seats = st.number_input("Total Seats", min_value=1, value=10)
    if st.button("Create Event"):
        payload = {
            "event_name": event_name,
            "venue": venue,
            "date": str(date),
            "total_seats": int(total_seats)
        }
        resp = requests.post(f"{API_URL}/events", json=payload)
        if resp.status_code == 200:
            st.success("Event created successfully!")
        else:
            st.error(resp.json().get("detail", "Error creating event."))

def book_event(event):
    st.header(f"Book Event: {event['event_name']}")
    user_name = st.text_input("Your Name")
    user_email = st.text_input("Your Email")
    seats_booked = st.number_input("Number of Seats", min_value=1, max_value=event["seats_available"], value=1)
    if st.button("Book Now"):
        payload = {
            "user_name": user_name,
            "user_email": user_email,
            "event_id": event["id"],
            "seats_booked": int(seats_booked)
        }
        resp = requests.post(f"{API_URL}/bookings", json=payload)
        if resp.status_code == 200:
            st.success("Booking successful!")
            st.session_state["page"] = "events"
        else:
            st.error(resp.json().get("detail", "Error booking event."))

def show_bookings():
    st.header("All Bookings (Admin)")
    resp = requests.get(f"{API_URL}/bookings")
    if resp.status_code == 200:
        bookings = resp.json().get("data", [])
        for booking in bookings:
            st.write(f"Name: {booking['user_name']}, Email: {booking['user_email']}, Event ID: {booking['event_id']}, Seats: {booking['seats_booked']}, Time: {booking['booking_time']}")
    else:
        st.error("Could not fetch bookings.")

def main():
    st.title("Student Task & Event Manager")
    menu = ["Events", "Create Event (Admin)", "View Bookings (Admin)"]
    if "page" not in st.session_state:
        st.session_state["page"] = "events"
    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None

    choice = st.sidebar.radio("Menu", menu)
    if choice == "Events":
        st.session_state["page"] = "events"
    elif choice == "Create Event (Admin)":
        st.session_state["page"] = "create_event"
    elif choice == "View Bookings (Admin)":
        st.session_state["page"] = "bookings"

    if st.session_state["page"] == "events":
        show_events()
    elif st.session_state["page"] == "create_event":
        create_event()
    elif st.session_state["page"] == "book":
        book_event(st.session_state["selected_event"])
    elif st.session_state["page"] == "bookings":
        show_bookings()

if __name__ == "__main__":
    main()