# A class representing a car available for rental.
class Car:
     # Initializes a new Car instance.
    def __init__(self, car_id, make, model, year, mileage, rate, available=True, min_days=1, max_days=30): 
        self.car_id = car_id
        self.make = make
        self.model = model
        self.year = year
        self.mileage = mileage
        self.rate = rate
        self.available = available
        self.min_days = min_days
        self.max_days = max_days
    def __str__(self):
        # Formats the car details into a readable string.
        availability = "Available" if self.available else "Rented"
        # returns a string representation of the car.
        return (f"[{self.car_id}] {self.make} {self.model} ({self.year}) | Mileage: {self.mileage} | "
                f"Rate: ${self.rate:.2f} | Rental Days: {self.min_days}-{self.max_days} | {availability}")
