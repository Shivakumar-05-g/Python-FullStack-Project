import streamlit as st
import requests

API_URL = "http://localhost:8000"

def register():
	st.subheader("Register")
	username = st.text_input("Username", key="reg_user")
	password = st.text_input("Password", type="password", key="reg_pass")
	if st.button("Register"):
		resp = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
		st.success(resp.json().get("message"))

def login():
	st.subheader("Login")
	username = st.text_input("Username", key="login_user")
	password = st.text_input("Password", type="password", key="login_pass")
	if st.button("Login"):
		resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
		data = resp.json()
		if "is_admin" in data:
			st.session_state["username"] = username
			st.session_state["is_admin"] = data["is_admin"]
			st.success("Login successful")
		else:
			st.error(data.get("detail", "Login failed"))

def seat_selection(event_id):
	resp = requests.get(f"{API_URL}/events/{event_id}/seats")
	seats = resp.json()
	available = [s for s, u in seats.items() if u is None]
	seat = st.selectbox("Select Seat", available)
	return seat

def payment(event_id, seat):
	amount = st.number_input("Amount", min_value=0.0, value=100.0)
	if st.button("Pay & Book"):
		resp = requests.post(f"{API_URL}/pay", json={
			"username": st.session_state["username"],
			"event_id": event_id,
			"seat": seat,
			"amount": amount
		})
		st.success(resp.json().get("message"))

def admin_dashboard():
	st.subheader("Admin Dashboard")
	if st.button("View Bookings"):
		resp = requests.get(f"{API_URL}/admin/bookings", params={"username": st.session_state["username"]})
		st.write(resp.json())
	st.subheader("Add Event")
	name = st.text_input("Event Name")
	seat_count = st.number_input("Seat Count", min_value=1, value=50)
	if st.button("Add Event"):
		resp = requests.post(f"{API_URL}/admin/events", params={
			"username": st.session_state["username"],
			"name": name,
			"seat_count": seat_count
		})
		st.success(resp.json().get("message"))

def main():
	st.title("E-Ticket Booking System")
	if "username" not in st.session_state:
		menu = ["Login", "Register"]
		choice = st.sidebar.selectbox("Menu", menu)
		if choice == "Login":
			login()
		else:
			register()
	else:
		st.write(f"Welcome, {st.session_state['username']}")
		event_id = 1  # Only one event for demo
		seat = seat_selection(event_id)
		payment(event_id, seat)
		if st.session_state.get("is_admin"):
			admin_dashboard()

if __name__ == "__main__":
	main()
