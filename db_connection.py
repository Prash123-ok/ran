import sqlite3
import os
import bcrypt

DB_PATH = "car_rental.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        mileage INTEGER NOT NULL,
        rate REAL NOT NULL,
        min_days INTEGER NOT NULL,
        max_days INTEGER NOT NULL,
        available BOOLEAN DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        days INTEGER NOT NULL,
        total_fee REAL DEFAULT 0 NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (car_id) REFERENCES cars(id),
        FOREIGN KEY (customer_name) REFERENCES users(username)
    )
    """)

    # Insert demo car data if empty
    cursor.execute("SELECT COUNT(*) FROM cars")
    if cursor.fetchone()[0] == 0:
        print("🚗 Inserting sample car data...")
        cars = [
            # (make, model, year, mileage, rate, min_days, max_days)
            ("Toyota", "Camry", 2020, 35000, 45.99, 1, 15),
            ("Honda", "Civic", 2019, 42000, 40.00, 2, 14),
            ("Ford", "Focus", 2018, 50000, 38.50, 1, 10),
            ("Chevrolet", "Malibu", 2021, 22000, 48.99, 3, 12),
            ("Nissan", "Altima", 2020, 31000, 44.50, 2, 14),
            ("Hyundai", "Elantra", 2019, 46000, 39.99, 1, 10),
            ("Kia", "Forte", 2021, 18000, 42.00, 1, 12),
            ("Mazda", "Mazda3", 2022, 12000, 50.00, 1, 15),
            ("Volkswagen", "Jetta", 2017, 55000, 35.99, 2, 10),
            ("Subaru", "Impreza", 2021, 27000, 47.25, 1, 13)
        ]
        cursor.executemany("""
            INSERT INTO cars (make, model, year, mileage, rate, min_days, max_days, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, cars)
        print("✅ Sample car data inserted.")

    # Insert demo admin and customer user if not exists
    users = [
        # (username, raw_password, role, email)
        ("admin", "admin123", "admin", "admin@example.com"),
        ("customer", "cust123", "customer", "customer@example.com")
    ]

    for username, raw_password, role, email in users:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (username, password, role, email)
                VALUES (?, ?, ?, ?)
            """, (username, hashed_pw, role, email))
            print(f"✅ Default user '{username}' added.")

    conn.commit()
    conn.close()
