#E-Ticket Booking System

An E-Ticket Booking System is a software application that allows users to book tickets for events like concerts, movies, or sports matches online. Users can create accounts, browse available events, select seats, and make bookings from anywhere using their computer or phone. The system keeps track of available seats to avoid double bookings and generates digital tickets that users can use to enter the event. Payments can be handled securely online. This system makes ticket buying easy, fast, and paperless.

Events table (event_id, event_name, venue, date, total_seats, seats_available)

Bookings table (booking_id, user_id, event_id, seats_booked, booking_time)



## Features

- User Information Captured at Booking: Users provide their name and email during booking without a separate registration system.

- Event Management: Ability to add, update, and manage events including venue, date, and seat availability.

- Seat Booking: Users can book a specified number of seats for a given event, with real-time checking of seat availability to prevent overbooking.

- Booking Confirmation: Each booking records the user details, event selected, number of seats booked, and booking timestamp.

- View Booking Details: Users can retrieve their booking details using their email or booking ID.

- Basic Admin Controls: Admin can manage events and monitor the bookings made.

- Prevent Double Booking: The system updates and checks seats_available to ensure no overbooking happens.

- Simple and Lightweight: Focuses on essential functionality using just two tables to keep development straightforward.

## Project Structure


E-TicketBooking/
|
|---src/            #core application logic
    |---logic.py    #Business logic and task
operations
|    |__db.py       #Database oprations
|
|---api/            #Backend API
|    |__main.py     #FastAPI endpoints
|
|---frontend/       #Frontend Application
|   |__app.py       #Streamlit web interface
|
|___requirements.txt    #python Dependencies
|
|___.env    #Python Variables

## Quick Start

## prerequisites

- python3.8 or higher
- A supabase Account
- Git(Push, Cloning)

### 1. Clone or Download the project 
# option 1:Clone with Git
git clone <repository-url>

# option 2: Download and Extract the Zip file

### 2. Install all required pyton packages
pip install -r requirements.txt

### 3. Set up Supabase Database
1.Create a Subapase Project:
2.Create the Tasks Table:
-Go to the sql Editor in your Supabase
dashboard
- Run this 

```sql

CREATE TABLE Events (
  event_id SERIAL PRIMARY KEY,
  event_name VARCHAR(255) NOT NULL,
  venue VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  total_seats INT NOT NULL,
  seats_available INT NOT NULL
);

CREATE TABLE Bookings (
  booking_id SERIAL PRIMARY KEY,
  user_name VARCHAR(100) NOT NULL,
  user_email VARCHAR(100) NOT NULL,
  event_id INT NOT NULL,
  seats_booked INT NOT NULL,
  booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES Events(event_id)
);


```sql