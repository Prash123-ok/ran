from db_connection import get_connection # Import database connection utility
import bcrypt # Import bcrypt for password hashing
import os # Import os for environment variable handling
from datetime import datetime # Import datetime for date handling
from services.email_service import send_email # Import email sending service

class RentalService: # Main service class for car rental operations
    def __init__(self): # Initialize the rental service
        self.conn = get_connection() # Get database connection 
        self.cursor = self.conn.cursor() # Create a cursor for executing SQL commands
        self.dry_run = os.getenv("EMAIL_DRY_RUN", "False").lower() == "true" # Check if dry run mode is enabled for email sending

    def register_user(self, username, password, role, email): # Register a new user in the system
        if not username or not password or not role or not email: # Check if all fields are provided
            print("All fields are required for registration.") 
            return False
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) # Hash the password using bcrypt
        try:
            # Insert the new user into the database
            self.cursor.execute(""" 
                INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?) 
            """, (username, hashed_pw, role, email))
            self.conn.commit()
            print(f"✔️User '{username}' registered successfully as '{role}'.") # Print registered success message
            return True
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False

    def login_user(self, username, password): # Authenticate a user by checking username and password
        self.cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,)) # Fetch the user's password and role from the database
        result = self.cursor.fetchone() # Get the first matching record
        if result:
            stored_hash, role = result
            try:
                if isinstance(stored_hash, str): # Ensure stored hash is a string
                    stored_hash = stored_hash.encode('utf-8') # Convert to bytes for bcrypt comparison
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash): # Check if the provided password matches the stored hash
                    return role
            except ValueError:
                print("❌ Invalid password format in database. Re-register the user.") # Handle potential ValueError if stored hash is not in expected format
                return None
        return None

    def add_car(self, make, model, year, mileage, rate, min_days, max_days): 
        # Add a new car to the rental inventory
        self.cursor.execute("""
            INSERT INTO cars (make, model, year, mileage, rate, min_days, max_days, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (make, model, year, mileage, rate, min_days, max_days))
        self.conn.commit()
        print(f"🚘 New car '{make} {model}' added successfully!")

    def update_car(self, car_id, mileage, rate):
        # Update the mileage and rate of an existing car
        self.cursor.execute(
            "UPDATE cars SET mileage = ?, rate = ? WHERE id = ?",
            (mileage, rate, car_id))
        self.conn.commit()
        print(f" Car ID {car_id} updated successfully.") 

    def delete_car(self, car_id):
        # Delete a car from the rental inventory
        self.cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        self.conn.commit()
        print(f"🗑️ Car ID {car_id} deleted.")

    def display_available_cars(self):
        # Display all available cars for rental
        self.cursor.execute("SELECT * FROM cars WHERE available = 1")
        cars = self.cursor.fetchall()
        if not cars:
            print("⛔ No available cars found.")
            return
        print("\n🚘 Available Cars:")
        for car in cars:
            print(f"[{car[0]}] {car[1]} {car[2]} ({car[3]}) | Mileage: {car[4]} | Rate: ${car[5]}")

    def book_car(self, customer_name, car_id, days):
        # Book a car for a customer
        self.cursor.execute("SELECT email FROM users WHERE username = ?", (customer_name,))
        email_row = self.cursor.fetchone() # Fetch the user's email based on their username
        if not email_row:
            print("❌ Email not found for user.")
            return
        email = email_row[0] # Extract the email from the fetched row

        self.cursor.execute("SELECT * FROM cars WHERE id = ? AND available = 1", (car_id,)) # Check if the car is available
        car = self.cursor.fetchone()  # Fetch the car details based on the provided car ID
        if car:
            if days < car[6] or days > car[7]: # Check if the requested rental days are within the allowed range
                print(f"🚫Days out of allowed range. Choose between {car[6]} and {car[7]} days.") 
                return
            total_cost = days * car[5]
            # Calculate the total rental cost based on the daily rate and number of days
            self.cursor.execute(""" 
                INSERT INTO bookings (customer_name, car_id, days, total_fee)
                VALUES (?, ?, ?, ?)
            """, (customer_name, car_id, days, total_cost))
            self.conn.commit()

            print(" Booking submitted successfully and is pending approval!")

            subject = "🧾Booking Received"
            body = (f"Hi {customer_name},\n\n"
                    f"Your booking for {car[1]} {car[2]} is pending approval.\n"
                    f"Rental days: {days}\nEstimated cost: ${total_cost}\n\n"
                    "You'll receive a confirmation soon.")
            send_email(email, subject, body, dry_run=self.dry_run)
        else:
            print("❌ Car not found or unavailable.")

    def view_bookings(self, customer_name=None): # View all bookings or filter by customer name
        if customer_name:
            self.cursor.execute("SELECT * FROM bookings WHERE customer_name = ?", (customer_name,))
        else:
            self.cursor.execute("SELECT * FROM bookings")
        bookings = self.cursor.fetchall()
        if not bookings:
            print("🙅🏻 No bookings found.")
            return
        print("\n📋 Bookings:")
        for b in bookings: # Loop through each booking and print its details
            print(f"[{b[0]}] {b[1]} → Car ID {b[2]} | {b[3]} days | Status: {b[5]} | Fee: ${b[4]}") 

    def view_pending_bookings(self): # View all pending bookings
        self.cursor.execute("SELECT * FROM bookings WHERE status = 'pending'")
        bookings = self.cursor.fetchall() # Fetch all bookings with status 'pending'
        if not bookings:
            print("🟡 No pending bookings.")
            return

        print("\n⌛ Pending Bookings:") 
        for b in bookings:
            print(f" [{b[0]}] {b[1]} → Car {b[2]} for {b[3]} days | Fee: ${b[4]}")

    def manage_booking(self, booking_id, approve=True): # Approve or reject a booking based on its ID
        status = 'approved' if approve else 'rejected'
        self.cursor.execute("SELECT customer_name, car_id, days FROM bookings WHERE id = ?", (booking_id,))
        booking = self.cursor.fetchone() # Fetch the booking details based on the provided booking ID
        if not booking:
            print(f"❌ Booking ID {booking_id} not found.")
            return
        customer_name, car_id, days = booking
        self.cursor.execute("SELECT make, model FROM cars WHERE id = ?", (car_id,))
        car = self.cursor.fetchone()
        car_desc = f"{car[0]} {car[1]}" if car else "your car"

        if approve:
            self.cursor.execute("UPDATE cars SET available = 0 WHERE id = ?", (car_id,))

        self.cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
        self.conn.commit()

        if approve:
            print(f"✅ Booking ID {booking_id} approved.")
        else:
            print(f"❌ Booking ID {booking_id} rejected.")

        if approve:
            self.cursor.execute("SELECT email FROM users WHERE username = ?", (customer_name,))
            user_email_row = self.cursor.fetchone()
            if user_email_row:
                user_email = user_email_row[0]
                subject = "✅ Booking Approved"
                body = (f"Hi {customer_name},\n\n"
                        f"Your booking for {car_desc} has been approved.\n"
                        f"Rental Duration: {days} days.\n\nThank you for choosing us!")
                send_email(user_email, subject, body, dry_run=self.dry_run)

    def generate_bill(self, booking_id):
        self.cursor.execute("""
            SELECT b.customer_name, b.car_id, b.days, b.total_fee, b.status,
                   c.make, c.model, c.year, c.rate
            FROM bookings b
            JOIN cars c ON b.car_id = c.id
            WHERE b.id = ?
        """, (booking_id,))
        booking = self.cursor.fetchone()

        if not booking or booking[4] != 'approved':
            print("❌ Bill can only be generated for approved bookings.")
            return

        customer_name, car_id, days, total_fee, _, make, model, year, rate = booking
        tax_rate = 0.10
        tax_amount = total_fee * tax_rate
        grand_total = total_fee + tax_amount

        bill = f"""
===== Car Rental Bill =====

Customer Name: {customer_name}
Car: {make} {model} ({year})
Rental Duration: {days} days
Rate per day: ${rate:.2f}
-----------------------------
Subtotal: ${total_fee:.2f}
Tax (10%): ${tax_amount:.2f}
-----------------------------
Total Amount Due: ${grand_total:.2f}

Status: Approved

Thank you for renting with us!
=============================
"""
        print("🧾 Generating bill...\n")
        print(bill)
        return bill

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("🔒 Database connection closed.")
