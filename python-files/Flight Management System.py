#!/usr/bin/env python
# coding: utf-8

# In[30]:


import csv
import pandas as pd
from collections import defaultdict


# ### 1. Data Loading and Preprocessing

# In[33]:


# Parse the AirlineResDB
def parse_alResDB(file_path):
    dt = {}
    current_relation = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(('--', '[', 'group:', 'description')):
                continue
            if line.endswith('= {'):
                current_relation = line.split('=')[0].strip()
                dt[current_relation] = {'attributes': [], 'rows': []}
                continue
            if current_relation and not dt[current_relation]['attributes']:
                parts = [col.strip() for col in line.split(',')]
                if not all(part.replace('.', '', 1).isdigit() for part in parts):
                    dt[current_relation]['attributes'] = parts
                continue
            if current_relation and line and not line.startswith('}'):
                clean_line = line.rstrip(',')
                row_dt = [field.strip() for field in clean_line.split(',')]
                dt[current_relation]['rows'].append(row_dt)
    return dt

airline_dt = parse_alResDB("AirlineResDB")
df = {table: pd.DataFrame(dt['rows'], columns=dt['attributes']) 
              for table, dt in airline_dt.items()}


# In[35]:


# Dataframes checking
df['Fare']


# ### 2. Define Data Structure

# In[38]:


# Flight information
class Flight:
    def __init__(self, flight_number, airline, weekdays):
        self.flight_number = flight_number
        self.airline = airline
        self.weekdays = weekdays
        self.legs = []

    def add_leg(self, leg):
        self.legs.append(leg)

    def __str__(self):
        return f"{self.flight_number} ({self.airline}) - {'Daily' if self.weekdays == 'Yes' else 'Weekly'}"


# In[40]:


# Represents the leg of a flight
class FlightLeg:
    def __init__(self, flight_number, leg_number, departure_airport, scheduled_departure_time, arrival_airport, scheduled_arrival_time):
        self.flight_number = flight_number
        self.leg_number = leg_number
        self.departure_airport = departure_airport
        self.scheduled_departure_time = scheduled_departure_time
        self.arrival_airport = arrival_airport
        self.scheduled_arrival_time = scheduled_arrival_time

    def __str__(self):
        return f"{self.flight_number} - Leg {self.leg_number}: {self.departure_airport} ({self.scheduled_departure_time}) -> {self.arrival_airport} ({self.scheduled_arrival_time})"


# In[42]:


# Represents a specific instance of a flight segment on a certain day
class LegInstance:
    def __init__(self, flight_number, leg_number, date, airplane_id, departure_airport, departure_time, arrival_airport, arrival_time):
        self.flight_number = flight_number
        self.leg_number = leg_number
        self.date = date
        self.airplane_id = airplane_id
        self.departure_airport = departure_airport
        self.departure_time = departure_time
        self.arrival_airport = arrival_airport
        self.arrival_time = arrival_time
        self.seats = []
        self.waitlist = Queue()

    def add_seat(self, seat):
        self.seats.append(seat)

    def get_available_seats(self):
        return [seat for seat in self.seats if not seat.is_reserved]

    def quick_sort_seats(self, seats):
        if len(seats) <= 1:
            return seats
        pivot = seats[len(seats)//2].seat_number
        left = [x for x in seats if x.seat_number < pivot]
        middle = [x for x in seats if x.seat_number == pivot]
        right = [x for x in seats if x.seat_number > pivot]
        return self.quick_sort_seats(left) + middle + self.quick_sort_seats(right)

    def print_sorted_seats(self):
        # Calculate remaining seats in each class
        total_seats = len(self.seats)
        first_class = [s for s in self.seats if s.seat_class == "First"]
        business_class = [s for s in self.seats if s.seat_class == "Business"]
        economy_class = [s for s in self.seats if s.seat_class == "Economy"]
        
        first_left = sum(1 for s in first_class if not s.is_reserved)
        business_left = sum(1 for s in business_class if not s.is_reserved)
        economy_left = sum(1 for s in economy_class if not s.is_reserved)
        
        # Printing seat availability information
        print("\n=== Seat available ===")
        print(f"First Class: {first_left}/{len(first_class)} Empty")
        print(f"Business Class: {business_left}/{len(business_class)} Empty") 
        print(f"Economy Class: {economy_left}/{len(economy_class)} Empty")
        
        # Original seat printing logic
        print("\n=== Seat Status (sorted by seat number)===")
        sorted_seats = self.quick_sort_seats(self.seats.copy())
        for seat in sorted_seats:
            status = "Booked" if seat.is_reserved else "Empty"
            print(f"Seat {seat.seat_number} ({seat.seat_class}): {status} {seat.passenger_name if seat.is_reserved else ''}")

    def binary_search_passenger(self, passenger_id):
        sorted_seats = self.quick_sort_seats([s for s in self.seats if s.is_reserved])
        low, high = 0, len(sorted_seats)-1
        while low <= high:
            mid = (low + high) // 2
            if sorted_seats[mid].passenger_name == passenger_id:
                return sorted_seats[mid]
            elif sorted_seats[mid].passenger_name < passenger_id:
                low = mid + 1
            else:
                high = mid - 1
        return None
  
    def book_seat(self, passenger):
        # Check if bookings have been made
        for seat in self.seats:
            if seat.is_reserved and seat.passenger_name == passenger.name:
                print(f"{passenger.name} seats have been reserved.")
                return
        
        # Allow passengers to choose their class
        while True:
            seat_class = input("Please select the class(First/Business/Economy): ").capitalize()
            if seat_class in ["First", "Business", "Economy"]:
                break
            print("Invalid class selection, please re-enter.")
        
        # Set passenger preferred class
        passenger.preferred_class = seat_class
        
        # Find available seats
        available = [s for s in self.get_available_seats() if s.seat_class == seat_class]
        
        if available:
            # Seats available
            seat = available[0]
            seat.reserve(passenger.name)
            passenger.update_status("Booked", self.flight_number)
            print(f"{passenger.name} successfully booked {seat_class} class in seat {seat.seat_number}")
        else:
            # Add to the waiting list
            self.waitlist.enqueue(passenger)
            passenger.update_status("Waiting", self.flight_number)
            print(f"{passenger.name} has been added to {seat_class} class waiting list")

    def cancel_reservation(self, passenger):
        for seat in self.seats:
            if seat.is_reserved and seat.passenger_name == passenger.name:
                seat.cancel()
                passenger.update_status("None")
                next_passenger = self.waitlist.dequeue()
                if next_passenger:
                    seat.reserve(next_passenger.name)
                    next_passenger.update_status("Booked", self.flight_number)
                    print(f"{next_passenger.name} placed from waiting list to seat {seat.seat_number}")
                return
        print(f"{passenger.name} does not have a reservation")

    def print_waitlist(self):
        if not self.waitlist.is_empty():
            print("Waiting List：")
            for idx, passenger in enumerate(self.waitlist.items, 1):
                seat_class = getattr(passenger, 'preferred_class', 'any')
                print(f"{idx}. {passenger.name} (Waiting for{seat_class}class)")
        else:
            print("The waiting list is empty.")


# In[44]:


# Airplane information
class Airplane:
    def __init__(self, airplane_id, airplane_type, total_seats):
        self.airplane_id = airplane_id
        self.airplane_type = airplane_type
        self.total_seats = total_seats

    def __str__(self):
        return f"Airplane {self.airplane_id} ({self.airplane_type}), number of seats: {self.total_seats}"


# In[46]:


# Describes the status of a specific seat on a flight
class Seat:
    def __init__(self, seat_number, seat_class):
        self.seat_number = seat_number
        self.seat_class = seat_class
        self.is_reserved = False
        self.passenger_name = None

    def reserve(self, passenger_name):
        if not self.is_reserved:
            self.is_reserved = True
            self.passenger_name = passenger_name
            return True
        return False

    def cancel(self):
        self.is_reserved = False
        self.passenger_name = None


# In[48]:


# Indicates a passenger's basic information and current booking status.
class Passenger:
    def __init__(self, name, passenger_id, phone=None, preferred_class=None):
        self.name = name
        self.passenger_id = passenger_id
        self.phone = phone
        self.preferred_class = preferred_class 
        self.booking_status = "None"
        self.flight_number = None

    def get_status(self):
        if self.booking_status == "None":
            return f"{self.name} no booking"
        elif self.booking_status == "Booked":
            return f"{self.name} has booked a flight {self.flight_number}"
        else:
            return f"{self.name} is in the flight {self.flight_number} waiting list."

    def update_status(self, status, flight_number=None):
        self.booking_status = status
        self.flight_number = flight_number


# In[50]:


# Queue data structure
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, passenger):
        self.items.append(passenger)

    def dequeue(self):
        return self.items.pop(0) if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def show(self):
        for idx, p in enumerate(self.items, 1):
            print(f"{idx}. {p.name} ({p.passenger_id})")


# In[52]:


# Tree data structure
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __str__(self):
        return str(self.value)


# In[54]:


# Build a flight tree structure based on the TreeNode class
class FlightTree:
    def __init__(self, root_flight):
        self.root = TreeNode(root_flight)

    def add_leg(self, flight_number, leg):
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            if isinstance(node.value, Flight) and node.value.flight_number == flight_number:
                node.add_child(TreeNode(leg))
                return True
            queue.extend(node.children)
        return False

    def print_tree(self):
        self._print_tree(self.root)

    def _print_tree(self, node, level=0):
        print("  "*level + "- " + str(node.value))
        for child in node.children:
            self._print_tree(child, level+1)


# ### 3. Flight System Main Class

# In[57]:


class FlightSystem:
    def __init__(self):
        self.flights = []
        self.leg_instances = []
        self.passengers = {}
        self.airplanes = {}
        self.airports = set()
        self.flight_tree = None


    def load_dt(self):
        # Load airplane data
        for _, row in df['Airplane'].iterrows():
            self.airplanes[row['Airplane_id']] = Airplane(
                row['Airplane_id'],
                row['Airplane_type'],
                int(row['Total_number_of_seats'])
            )
        
        # Loading flight data
        for _, row in df['Flight'].iterrows():
            self.flights.append(Flight(
                row['Flight_number'],
                row['Airline'],
                row['Weekdays']
            ))
        
        # Load flight leg data
        for _, row in df['Flight_leg'].iterrows():
            flight = next((f for f in self.flights if f.flight_number == row['Flight_number']), None)
            if flight:
                flight.add_leg(FlightLeg(
                    row['Flight_number'],
                    int(row['Leg_number']),
                    row['Departure_airport_code'],
                    row['Scheduled_departure_time'],
                    row['Arrival_airport_code'],
                    row['Scheduled_arrival_time']
                ))
        
        # Load flight leg instance data
        for _, row in df['Leg_instance'].iterrows():
            leg_instance = LegInstance(
                row['Flight_number'],
                int(row['Leg_number']),
                row['Date:date'],
                row['Airplane_id'],
                row['Departure_airport_code'],
                row['Departure_time'],
                row['Arrival_airport_code'],
                row['Arrival_time']
            )
            
            # Add seats
            airplane = self.airplanes.get(row['Airplane_id'])
            if airplane:
                total_seats = airplane.total_seats
                first_class = int(total_seats * 0.1)
                business_class = int(total_seats * 0.3)
                for i in range(1, total_seats+1):
                    seat_class = "First" if i <= first_class else "Business" if i <= first_class+business_class else "Economy"
                    leg_instance.add_seat(Seat(f"{i}{chr(65 + (i % 26))}", seat_class))
            
            self.leg_instances.append(leg_instance)
        
        # Load reservation data
        for _, row in df['Seat_reservation'].iterrows():
            passenger_id = f"{row['Customer_name']}_{row['Customer_phone']}"
            if passenger_id not in self.passengers:
                self.passengers[passenger_id] = Passenger(
                    row['Customer_name'],
                    passenger_id,
                    row['Customer_phone']
                )
            
            leg_instance = next(
                (li for li in self.leg_instances 
                 if li.flight_number == row['Flight_number'] 
                 and li.leg_number == int(row['Leg_number'])
                 and li.date == row['Date:date']), 
                None
            )
            
            if leg_instance:
                seat = next((s for s in leg_instance.seats if s.seat_number == row['Seat_number']), None)
                if seat:
                    seat.reserve(row['Customer_name'])
                    self.passengers[passenger_id].update_status("Booked", row['Flight_number'])
        
        # Building the flight tree
        if self.flights:
            self.flight_tree = FlightTree(self.flights[0])
            for flight in self.flights[1:]:
                self.flight_tree.root.add_child(TreeNode(flight))
            for flight in self.flights:
                for leg in flight.legs:
                    self.flight_tree.add_leg(flight.flight_number, leg)

    def find_flights(self, source_city, dest_city, date):
        source_airports = [row['Airport_code'] for _, row in df['Airport'].iterrows() 
                          if row['City'] == source_city]
        dest_airports = [row['Airport_code'] for _, row in df['Airport'].iterrows() 
                        if row['City'] == dest_city]
        
        available_flights = []
        for leg_instance in self.leg_instances:
            if (leg_instance.departure_airport in source_airports and
                leg_instance.arrival_airport in dest_airports and
                leg_instance.date == date):
                available_flights.append(leg_instance)
        
        return available_flights

    def print_flight_info(self, flight_number):
        flight = next((f for f in self.flights if f.flight_number == flight_number), None)
        if not flight:
            print(f"Not found flight {flight_number}")
            return
        
        print(f"\nflight {flight_number} information:")
        print(flight)
        
        print("\nFlight leg information:")
        for leg in flight.legs:
            print(leg)
            instances = [li for li in self.leg_instances 
                        if li.flight_number == flight_number 
                        and li.leg_number == leg.leg_number]
            for li in instances:
                print(f"  Instance Date: {li.date}, Airplane: {li.airplane_id}")
                li.print_sorted_seats()
                li.print_waitlist()

    def menu(self):
        print("\n===== Flight Booking System =====")
        print("1. View All Flights")
        print("2. View Flight Tree Structure")
        print("3. Check Flight Information")
        print("4. Check Flights Between Cities")
        print("5. Book a Seat")
        print("6. Booking Cancellation")
        print("7. Check Passenger Status")
        print("8. Exit")
        
        while True:
            choice = input("\nPlease enter your options (1-8): ")
            
            if choice == "1":
                print("\nAll flights:")
                for flight in self.flights:
                    print(flight)
            
            elif choice == "2":
                if self.flight_tree:
                    print("\nFlight Tree Structure:")
                    self.flight_tree.print_tree()
                else:
                    print("Flight tree not initialised.")
            
            elif choice == "3":
                flight_number = input("Please enter flight number: ")
                self.print_flight_info(flight_number)
            
            elif choice == "4":
                source = input("Please enter a departure city: ")
                dest = input("Please enter a destination city: ")
                date = input("Please enter a date(YYYY-MM-DD): ")
                flights = self.find_flights(source, dest, date)
                print(f"\nFound {len(flights)} flights:")
                for flight in flights:
                    print(f"{flight.flight_number} - {flight.departure_airport} -> {flight.arrival_airport}")
                    print(f"  Time: {flight.departure_time} - {flight.arrival_time}")
                    print(f"  Airplane: {flight.airplane_id}")
            
            elif choice == "5":
                flight_number = input("Please enter flight number: ")
                leg_number = input("Please enter the flight leg number: ")
                date = input("Please enter a date(YYYY-MM-DD): ")
                name = input("Please enter passenger's name: ")
                phone = input("Please enter a passenger's phone number: ")
                
                passenger_id = f"{name}_{phone}"
                if passenger_id not in self.passengers:
                    self.passengers[passenger_id] = Passenger(name, passenger_id, phone)
                
                leg_instance = next(
                    (li for li in self.leg_instances 
                     if li.flight_number == flight_number 
                     and str(li.leg_number) == leg_number 
                     and li.date == date), 
                    None
                )
                
                if leg_instance:
                    leg_instance.book_seat(self.passengers[passenger_id])
                else:
                    print("Invalid flight information.")
            
            elif choice == "6":
                flight_number = input("Please enter flight number: ")
                leg_number = input("Please enter the flight leg number: ")
                date = input("Please enter a date(YYYY-MM-DD): ")
                name = input("Please enter passenger's name: ")
                phone = input("Please enter a passenger's phone number: ")
                
                passenger_id = f"{name}_{phone}"
                passenger = self.passengers.get(passenger_id)
                
                if passenger:
                    leg_instance = next(
                        (li for li in self.leg_instances 
                         if li.flight_number == flight_number 
                         and str(li.leg_number) == leg_number 
                         and li.date == date), 
                        None
                    )
                    if leg_instance:
                        # First check whether the passenger has a booking
                        has_reservation = any(
                            seat.is_reserved and seat.passenger_name == passenger.name
                            for seat in leg_instance.seats
                        )
                        
                        if has_reservation:
                            leg_instance.cancel_reservation(passenger) 
                            print(f"Successfully cancelled the booking of {passenger.name} in flight {flight_number}.")  
                        else:
                            print(f"{passenger.name} has not booked a seat on this flight.")
                    else:
                        print("Invalid flight information.")
                else:
                    print("Passenger not found.")
            
            elif choice == "7":
                name = input("Please enter passenger's name: ")
                phone = input("Please enter a passenger's phone number: ")
                passenger_id = f"{name}_{phone}"
                passenger = self.passengers.get(passenger_id)
                if passenger:
                    print(passenger.get_status())
                else:
                    print("Passenger not found.")
            
            elif choice == "8":
                print("Exit system.")
                break
            
            else:
                print("Invalid input, please try again.")

# Main program
if __name__ == "__main__":
    system = FlightSystem()
    system.load_dt()
    
    print("=== Flight Booking System ===")
    print(f"{len(system.flights)} flights loaded")
    print(f"{len(system.leg_instances)} instances flight legs loaded")
    print(f"{len(system.passengers)} passenger records loaded")
    
    system.menu()

