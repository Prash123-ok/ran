from db_connection import initialize_database # Import the function to initialize the database
from services.rental_service import RentalService # Import the RentalService class
import os # For environment variable management
import getpass # For secure password input

# Initialize the database (creates tables and seeds cars)
initialize_database()

def auth_menu(service): # Function to handle user authentication and registration
    while True: # Loop until a valid login or registration is completed
        print("\n=== Welcome to Car Rental System ===") # Display welcome message
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Select option: ")

        # Login option
        if choice == '1': 
            username = input("Enter username to login: ")
            password = getpass.getpass("Enter password: ")
            role = service.login_user(username, password)
            if role:
                print(f"Logged in as '{username}' ({role})")
                return username, role
            else:
                print("Invalid username or password. Please try again or register.")

       # Registration option
        elif choice == '2': 
            username = input("Enter new username to register: ") 
            email = input("Enter your email address: ")
            while True:
                password = getpass.getpass("Enter password: ")
                password_confirm = getpass.getpass("Confirm password: ")
                if password != password_confirm:
                    print("Passwords do not match. Try again.")
                elif len(password) < 6:
                    print("Password must be at least 6 characters long.")
                else:
                    break
            role = input("Enter role (admin/customer): ").lower() # Get user role input
            if role not in ['admin', 'customer']: # Validate role input
                print("Invalid role. Defaulting to 'customer'.") # Default to customer if invalid role
                role = 'customer'
            registered = service.register_user(username, password, role, email)
            if registered:
                print(f"✅ User '{username}' registered as {role}. You can now login.")
                return username, role
            else:
                print("❌ Registration failed. Username may already exist.")

        elif choice == '3':
            print("Goodbye!")
            exit(0)

        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def clean_int_input(prompt): # Function to clean and convert integer input
    raw = input(prompt) # Prompt user for input
    return int(''.join(filter(str.isdigit, raw))) # Convert input to integer by filtering out non-digit characters

def clean_float_input(prompt): # Function to clean and convert float input
    raw = input(prompt) # Prompt user for input
    return float(''.join(ch for ch in raw if ch.isdigit() or ch == '.')) # Convert input to float by filtering out non-digit characters except for the decimal point

def main_menu(): # Main function to display the main menu and handle user interactions
    service = RentalService() # Create an instance of the RentalService class
    username, role = auth_menu(service) # Authenticate user and get their role

    while True:
        print("\n=== Main Menu ===")
        if role == 'admin':
            print("1. Add Car")
            print("2. Update Car")
            print("3. Delete Car")
            print("4. Show Available Cars")
            print("5. View Bookings")
            print("6. Approve/Reject Bookings")
            print("7. Exit")
        else:
            print("1. Show Available Cars")
            print("2. Book a Car")
            print("3. View My Bookings")
            print("4. Generate/View Bill")
            print("5. Exit")

        choice = input("Enter your choice: ")

        if role == 'admin':
            if choice == '1':
                print("\n-- Add New Car --")
                make = input("Car make (e.g. Toyota): ")
                model = input("Car model (e.g. Camry): ")
                year = clean_int_input("Manufacture year: ")
                mileage = clean_int_input("Current mileage: ")
                rate = clean_float_input("Daily rental rate ($): ")
                min_days = clean_int_input("Minimum rental days: ")
                max_days = clean_int_input("Maximum rental days: ")
                service.add_car(make, model, year, mileage, rate, min_days, max_days)

            elif choice == '2':
                car_id = clean_int_input("Car ID to update: ")
                mileage = clean_int_input("New mileage: ")
                rate = clean_float_input("New daily rate: ")
                service.update_car(car_id, mileage, rate)

            elif choice == '3':
                car_id = clean_int_input("Car ID to delete: ")
                service.delete_car(car_id)

            elif choice == '4':
                service.display_available_cars()

            elif choice == '5':
                service.view_bookings()

            elif choice == '6':
                service.view_pending_bookings()
                booking_id = clean_int_input("Enter Booking ID to manage: ")
                action = input("Approve or Reject? (a/r): ").lower()
                if action in ['a', 'r']:
                    service.manage_booking(booking_id, approve=(action == 'a'))
                else:
                    print("Invalid action. Please enter 'a' or 'r'.")

            elif choice == '7':
                break
            else:
                print("Invalid choice, please enter a number 1-7.")

        else:  # customer menu
            if choice == '1':
                service.display_available_cars()

            elif choice == '2':
                car_id = clean_int_input("Car ID: ")
                days = clean_int_input("Rental days: ")
                service.book_car(username, car_id, days)

            elif choice == '3':
                service.view_bookings(customer_name=username)

            elif choice == '4':
                booking_id = clean_int_input("Enter your Booking ID to generate/view bill: ")
                bill = service.generate_bill(booking_id)
                if bill:
                    save = input("Save bill to text file? (y/n): ").lower()
                    if save == 'y':
                        filename = f"bill_booking_{booking_id}.txt"
                        with open(filename, "w") as f:
                            f.write(bill)
                        print(f"Bill saved as {filename}")

            elif choice == '5':
                break
            else:
                print("Invalid choice, please enter a number 1-5.")

    service.close()
    print("Goodbye,See You Again!!!") # End the program

if __name__ == "__main__":
    main_menu()
