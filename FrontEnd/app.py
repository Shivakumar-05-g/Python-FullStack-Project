import streamlit as st
import requests
from requests.exceptions import RequestException
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Ticket Booking System", layout="centered")


def _safe_request_get(url, timeout=5):
    try:
        resp = requests.get(url, timeout=timeout)
    except RequestException as e:
        return None, f"Connection error: {e}"
    try:
        data = resp.json()
    except Exception:
        return None, f"Invalid JSON response (status {resp.status_code}): {resp.text}"
    return resp, data


def _safe_request_post(url, json=None, timeout=5):
    try:
        resp = requests.post(url, json=json, timeout=timeout)
    except RequestException as e:
        return None, f"Connection error: {e}"
    try:
        data = resp.json()
    except Exception:
        return None, f"Invalid JSON response (status {resp.status_code}): {resp.text}"
    return resp, data


def show_events():
    st.header("Available Events")
    resp, parsed = _safe_request_get(f"{API_URL}/events")
    if resp is None:
        st.error(parsed)
        return

    if resp.status_code != 200:
        msg = parsed.get("detail") if isinstance(parsed, dict) else parsed
        st.error(f"Could not fetch events: {msg}")
        return

    events = parsed.get("data") if isinstance(parsed, dict) else []
    if not events:
        st.info("No events available.")
        return

    for event in events:
        # Defensive access — event may be dict-like with different keys
        eid = event.get("id") or event.get("event_id")
        name = event.get("event_name") or event.get("name") or "Unnamed Event"
        venue = event.get("venue", "Unknown venue")
        date = event.get("date", "")
        total = event.get("total_seats", event.get("total", "-"))
        avail = event.get("seats_available", event.get("available", 0))

        st.subheader(name)
        st.write(f"Venue: {venue}")
        st.write(f"Date: {date}")
        st.write(f"Total Seats: {total}")
        st.write(f"Seats Available: {avail}")

        if avail and int(avail) > 0:
            if st.button(f"Book for {name}", key=f"book_{eid}"):
                st.session_state["selected_event"] = event
                st.session_state["page"] = "book"
        else:
            st.info("Sold out or seats unavailable.")


def create_event():
    st.header("Create New Event (Admin)")
    event_name = st.text_input("Event Name")
    venue = st.text_input("Venue")
    date = st.date_input("Date", value=datetime.date.today())
    total_seats = st.number_input("Total Seats", min_value=1, value=10)
    if st.button("Create Event"):
        payload = {
            "event_name": event_name,
            "venue": venue,
            "date": date.isoformat() if isinstance(date, datetime.date) else str(date),
            "total_seats": int(total_seats),
        }
        resp, parsed = _safe_request_post(f"{API_URL}/events", json=payload)
        if resp is None:
            st.error(parsed)
            return
        if resp.status_code == 200:
            st.success("Event created successfully!")
        else:
            detail = parsed.get("detail") if isinstance(parsed, dict) else parsed
            st.error(detail or "Error creating event.")


def book_event(event):
    st.header(f"Book Event: {event.get('event_name') or event.get('name')}")
    user_name = st.text_input("Your Name")
    user_email = st.text_input("Your Email")
    avail = event.get("seats_available", event.get("available", 0))
    try:
        avail_int = int(avail)
    except Exception:
        avail_int = 0

    seats_booked = st.number_input("Number of Seats", min_value=1, max_value=max(1, avail_int), value=1)
    if st.button("Book Now"):
        if avail_int <= 0:
            st.error("No seats available for this event.")
            return
        payload = {
            "user_name": user_name,
            "user_email": user_email,
            "event_id": event.get("id") or event.get("event_id"),
            "seats_booked": int(seats_booked),
        }
        resp, parsed = _safe_request_post(f"{API_URL}/bookings", json=payload)
        if resp is None:
            st.error(parsed)
            return
        if resp.status_code == 200:
            st.success("Booking successful!")
            st.session_state["page"] = "events"
        else:
            detail = parsed.get("detail") if isinstance(parsed, dict) else parsed
            st.error(detail or "Error booking event.")


def show_bookings():
    st.header("All Bookings (Admin)")
    resp, parsed = _safe_request_get(f"{API_URL}/bookings")
    if resp is None:
        st.error(parsed)
        return
    if resp.status_code != 200:
        msg = parsed.get("detail") if isinstance(parsed, dict) else parsed
        st.error(f"Could not fetch bookings: {msg}")
        return

    bookings = parsed.get("data") if isinstance(parsed, dict) else []
    if not bookings:
        st.info("No bookings found.")
        return

    for booking in bookings:
        st.write(
            f"Name: {booking.get('user_name')}, Email: {booking.get('user_email')}, Event ID: {booking.get('event_id')}, Seats: {booking.get('seats_booked')}, Time: {booking.get('booking_time')}"
        )


def main():
    global API_URL
    st.title("Ticket Booking System")
    # Allow runtime override of API URL for debugging (localhost vs 127.0.0.1)
    if "api_url" not in st.session_state:
        st.session_state["api_url"] = API_URL
    st.session_state["api_url"] = st.sidebar.text_input("API URL", value=st.session_state["api_url"]) or API_URL

    # use the runtime API URL in the module-level variable for compatibility
    API_URL = st.session_state["api_url"]
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
        # Defensive: selected_event might be None
        if st.session_state.get("selected_event"):
            book_event(st.session_state["selected_event"])
        else:
            st.info("Please select an event to book from the Events page.")
    elif st.session_state["page"] == "bookings":
        show_bookings()


if __name__ == "__main__":
    main()