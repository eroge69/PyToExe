# QUERY FUNCTIONS REMAINING

import sys

# global lists
global_vehicles = [] # [ [1, brand, mileage, rental, maint, avlbl], [], [] ]
global_transactions = [] # [ [cust name, car ID, duration, payable rent, maint, open / closed transaction ], [], [] ]
global_operations = [] # [ [cust, car ID, late fee, maint fee, clean fee], [], ]
global_vehicle_maintenance = [] # [ car ID, long term maintenance cost ]

# safe input, so that no user can easily break system with incorrect input types or formats or whatever
# default accepted type is str, just like input().
def safe_input(prompt, expected_type=str, allow_empty=False, allowed_values=None):
    while True: # while loop, so it keeps asking for input
        user_input = input(prompt).strip()
        if not allow_empty and user_input == "":
            print("Input cannot be empty")
            continue
        try: # check for input type here
            if expected_type == int:
                value = int(user_input)
            elif expected_type == float:
                value = float(user_input)
            else:
                value = user_input

            if allowed_values and value not in allowed_values:
                print(f"Input must be one of: {', '.join(map(str, allowed_values))}")
                continue
            return value
        except ValueError: # all other error types, it prints this
            print("Invalid input.")

# class definition for vehicle
class Vehicle:
    def __init__(self, vehicle_id, brand_model, mileage, rental, maintenance, availability, maintenance_status):
        self.vehicle_id = vehicle_id
        self.brand_model = brand_model
        self.mileage = mileage
        self.rental_price = rental
        self.maintenance_cost_per_km = maintenance
        self.availability = availability
        self.maintenance_status = maintenance_status
    def set_availability(self, status):
        self.availability = status
    def update_mileage(self, extra):
        self.mileage = self.mileage + extra
    def get_rental(self):
        return self.rental_price
    def get_mileage(self):
        return self.mileage
    def get_maintenance(self):
        return self.maintenance_cost_per_km
    def get_availability(self):
        return self.availability
    def set_maintenance_status(self, maint_status):
        self.maintenance_status = maint_status

def show_inventory():
    headers = ["ID", "Brand and Model", "Mileage", "Rental", "Maint/km", "Available"]
    
    # Prepare rows, first row is headers, then vehicle data
    rows = [headers]
    for v in global_vehicles:
        rows.append([
            str(v.vehicle_id),
            str(v.brand_model),
            str(v.mileage),
            f"{v.rental_price:.2f}",
            f"{v.maintenance_cost_per_km:.2f}",
            "Yes" if v.availability else "No"
        ])
    
    # Calculate max width for each column
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    
    # Print rows
    for row in rows:
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(line)
        if row == headers:
            print("-+-".join("-" * w for w in col_widths))  # separator after header


def add_vehicle_helper(vehicle_id, brand_model, mileage, rental, maintenance, availability, maintenance_status):
    v = Vehicle(vehicle_id, brand_model, mileage, rental, maintenance, availability, maintenance_status)
    global_vehicles.append(v)

def add_vehicle():
    print("Enter Vehicle Details")
    print("")
    vehicle_id = safe_input("ID..\n.", int)
    brand_model = safe_input("Brand and Model...\n", str)
    mileage = safe_input("Mileage...\n", float)
    rental = safe_input("Rental Price per Day...\n", float)
    maintenance = safe_input("Maintenance Price per km...\n", float)
    availability = safe_input("Availability...\n", int)
    if availability != 1 and availability != 0:
        print("Incorrect Input")
        return
    maintenance_status = 0
    if mileage > 10000:
        maintenance_status = 1
    add_vehicle_helper(vehicle_id, brand_model, mileage, rental, maintenance, availability, maintenance_status)

def initialise_cars():
    add_vehicle_helper(1, "Ford Focus", 200, 20, 1, 1, 0)
    add_vehicle_helper(2, "Ferrari F50", 4500, 110, 5, 1, 0)
    add_vehicle_helper(3, "Fiat Punto", 3000, 15, 1, 1, 0)
    add_vehicle_helper(4, "Suzuki Swift", 9000, 11.5, 1, 1, 0)
    add_vehicle_helper(5, "Toyota Carris", 11000, 35, 2, 1, 1)
    add_vehicle_helper(6, "Ford F350", 15000, 25, 0.5, 1, 1)
    add_vehicle_helper(7, "Cadillac Eldorado", 5000, 25, 1, 1, 0)
    add_vehicle_helper(8, "Panoz GTR", 2500, 160, 8, 1, 0)
    add_vehicle_helper(9, "Mustang Cruiser", 9000, 45, 3.5, 1, 0)
    add_vehicle_helper(10, "Mustang Fastback", 7500, 70, 1, 1, 0)
    
def vehicle_exists(vehicle_id):
    return any(v.vehicle_id == vehicle_id for v in global_vehicles)

def set_availability_by_id(vehicle_id, status):
    for v in global_vehicles:
        if v.vehicle_id == vehicle_id:
            v.set_availability(status)
            return 1
    return 0

def update_mileage_by_id(ID, extra):
    for v in global_vehicles:
        if v.vehicle_id == ID:
            v.update_mileage(extra)
            return 1
    return 0

def get_vehicle_info_by_id(ID, need):
    for v in global_vehicles:
        if v.vehicle_id == ID:
            if need == 1:
                return v.brand_model
            if need == 2:
                return v.mileage
            if need == 3:
                return v.rental_price
            if need == 4:
                return v.maintenance_cost_per_km
            if need == 5:
                return v.availability
            if need == 6:
                return v.maintenance_status
            
def set_vehicle_maint_status_by_id(ID, value):
    for v in global_vehicles:
        if v.vehicle_id == ID:
            v.set_maintenance_status(1)
            return 1
    return 0

def book():
    name = safe_input("Enter Customer Name\n", str)
    vid = safe_input("Enter Vehicle ID\n", int)
    if get_vehicle_info_by_id(vid, 5) == 0:
        print("Vehicle Either Not Available To Rent At This Moment, Or Already Rented.")
        return
    if vehicle_exists(vid) != 1:
        print("Invalid Vehicle ID. Try Again.")
        return
    days = safe_input("How long does customer want to rent it for in days\n", int)
    if days < 0:
        print("Number of days must be non-negative.")
        return
    km = safe_input("How many km does customer expect to drive?\n", float)
    if km < 0:
        print("km must be non-negative.")
        return
    
    rental = get_vehicle_info_by_id(vid, 3)
    maint = get_vehicle_info_by_id(vid, 4)
    print("Expected Cost = Rental(", days * rental, ")", "+ Maintenance(",km * maint, ")", "+ Cleaning Fee (20)")
    print("Expected Total Cost = ", days * rental + km * maint + 20)
    
    # for now, keeping expected maintenance per km. will calculate actual at return
    # opening the transaction (1)
    global_transactions.append([name, vid, days, days * rental, km * maint, 1])
    
    # update availability to 0
    set_availability_by_id(vid, 0)
    
    print("Vehicle Booked")
    
    return

def return_vehicle():
    name = safe_input("Enter Customer Name\n", str)
    # check if customer is valid
    cust_found = 0
    for cust in global_transactions:
        if cust[0] == name:
            cust_found = 1
            break
    if cust_found == 0:
        print("Invalid Customer Name")
        return
    
    vid = safe_input("Enter Vehicle ID\n", int)
    if vehicle_exists(vid) != 1: # if vehicle is even a vehicle
        print("Invalid Vehicle ID. Try Again.")
        return
    car_found_with_cust = 0 # if car is found with customer
    for cust in global_transactions:
        if cust[0] == name:
            if cust[1] == vid:
                if cust[5] == 1: # if transaction is still open, only then a returnable vehicle can be found
                    car_found_with_cust = 1
    if car_found_with_cust == 0:
        print("Customer does not possess this vehicle. Try Again.")
        return
    
    days = safe_input("How long did customer actually rent it for in days?\n", int)
    if days < 0:
        print("Number of days must be non-negative.")
        return
    # late charges calculation per vehicle ID and customer. 10 per day delay
    late_fee = 0
    cleaning_fee = 20
    for cust in global_transactions:
        if cust[0] == name and cust[1] == vid and cust[5] == 1:
            if days > cust[2]:
                late_fee = 10 * (days - cust[2])
    
    km = safe_input("How many km did customer actually drive?\n", float)
    if km < 0:
        print("km must be non-negative.")
        return
    
    # calculate costs
    rental = get_vehicle_info_by_id(vid, 3)
    maint = get_vehicle_info_by_id(vid, 4)
    print("Rental Cost =", days * rental)
    print("Operational Costs = Late Fee(",late_fee,") + Cleaning Fee (", cleaning_fee,") + Maintenance (", km * maint, ")")
    print("Total Cost =", days*rental + late_fee + cleaning_fee + km*maint)
    
    # update transactions and operations
    for cust in global_transactions:
        if cust[0] == name and cust[1] == vid and cust[5] == 1: # if name, id matches, and if transaction is an open one
            cust[2] = days
            cust[3] = days * rental
            cust[4] = km * maint
            # close (0) the transaction
            cust[5] = 0
    # global_transactions.append([name, vid, days, days * rental, km * maint])
    global_operations.append([name, vid, late_fee, km*maint, cleaning_fee])
    
    # update vehicle details
    set_availability_by_id(vid, 1)
    update_mileage_by_id(vid, km)
    if get_vehicle_info_by_id(vid, 2) > 10000: # if vehicle crosses 10,000km, then long term maintenance needed
        # update maintenance_availiability to 1
        set_vehicle_maint_status_by_id(vid, 1)
    
    print("Vehicle Returned")
    
    return

# maintenance needed for each vehicle beyond every 10000
def show_maintenance():
    headers = ["ID", "Brand and Model", "Mileage", "Maint/km", "Maintenance Needed"]
    
    # Prepare rows, first row is headers, then vehicle data
    rows = [headers]
    for v in global_vehicles:
        rows.append([
            str(v.vehicle_id),
            str(v.brand_model),
            str(v.mileage),
            f"{v.maintenance_cost_per_km:.2f}",
            "Yes" if v.maintenance_status == 1 else "No"
        ])
    
    # Calculate max width for each column
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    
    # Print rows
    for row in rows:
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(line)
        if row == headers:
            print("-+-".join("-" * w for w in col_widths))  # separator after header
            
    rows = []
    return

def show_transactions():
    
    headers = ["Customer Name", "Car ID", "Rent Duration", "Payable Rent", "Payable Maintenance"]
    
    # Prepare rows, first row is headers, then vehicle data
    rows = [headers]
    for c in global_transactions:
        rows.append([
            str(c[0]) + "(expected)" if c[5] == 1 else str(c[0]), # if transaction is still open, it means that the vehicle is not yet returned
            str(c[1]),
            str(c[2]),
            f"{c[3]:.2f}",
            f"{c[4]:.2f}",
        ])
    
    # Calculate max width for each column
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    
    # Print rows
    for row in rows:
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(line)
        if row == headers:
            print("-+-".join("-" * w for w in col_widths))  # separator after header
            
    rows = []
    
    return

def financial_revenue():
    total_payable = 0
    for cust in global_transactions:
        total_payable = total_payable + cust[3] + cust[4] # adding rental + maintenance cost (assuming there is no warranty or such, included in the business, and the customer has to undertake all expenses)
    print("Total Revenue =", total_payable)
    return
def financial_ops():
    total_op = 0
    for cust in global_operations:
        total_op = total_op + cust[2] + cust[3] + cust[4] # maintenance + cleaning + late fees
    print("Total Operational Cost =", total_op)
def financial_profit():
    total_payable = 0
    for cust in global_transactions:
        total_payable = total_payable + cust[3] + cust[4]
    total_op = 0
    for cust in global_operations:
        total_op = total_op + cust[2] + cust[3] + cust[4]
    print("Total Profit =", total_payable - total_op)
def financial_avg_mileage():
    car_mileage_avg = [] # [ [car ID, avg mileage per trip], [], ]
    for v in global_vehicles:
        car_id = v.vehicle_id
        maint_per_km = v.maintenance_cost_per_km
        trips = [t[4] for t in global_transactions if t[1] == car_id]
        if trips:
            total_mileage = sum(trip / maint_per_km for trip in trips)
            avg_mileage = total_mileage / len(trips)
            car_mileage_avg.append([car_id, avg_mileage])
        else:
            car_mileage_avg.append([car_id, 0])
    car_mileage_avg = sorted(car_mileage_avg, key=lambda x: x[1], reverse=True) # sorting from highest to lowest
    # display table
    headers = ["Car ID", "Average Mileage Driven by Customers"]
    
    # Prepare rows, first row is headers, then vehicle data
    rows = [headers]
    for i in car_mileage_avg:
        rows.append([
            str(i[0]),
            str(i[1]),
        ])
            
    # Calculate max width for each column
    col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
            
    # Print rows
    for row in rows:
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(line)
        if row == headers:
            print("-+-".join("-" * w for w in col_widths))  # separator after header

def financial_metrics():
    while True:
        print("")
        print("1. Show total revenue")
        print("2. Show total operational cost")
        print("3. Show total profit")
        print("4. Show average mileage driven by customers per vehicle")
        print("5. Show full financial report")
        print("6. Query metrics")
        print("7. Back")
        menu = safe_input("", int)
        if menu == 1:
            financial_revenue()
        elif menu == 2:
            financial_ops()
        elif menu == 3:
            financial_profit()
        elif menu == 4:
            financial_avg_mileage()
        elif menu == 5:
            financial_revenue()
            print("")
            financial_ops()
            print("")
            financial_profit()
            print("")
            financial_avg_mileage()
        elif menu == 6:
            print("What do you want to query?")
            print("1. Rentals per vehicle")
            print("2. Total revenue per vehicle")
            print("3. Total maintenance per vehicle")
            print("4. Profitability (Revenue vs Maintenance) per vehicle")
            print("5. Average Profit per rental per vehicle")
            menu = safe_input("", int)
            if menu == 1:
                rental_counts = []  # [ [car_id, rental_count], ... ]
                for v in global_vehicles:
                    car_id = v.vehicle_id
                    count = sum(1 for t in global_transactions if t[1] == car_id)
                    rental_counts.append([car_id, count])
                rental_counts = sorted(rental_counts, key=lambda x: x[1], reverse=True) # sorting from highest to lowest
                # Printing table now
                headers = ["Vehicle ID", "Total Rentals"]
                rows = [headers]
                for i in rental_counts:
                    rows.append([
                        str(i[0]),
                        str(i[1]),
                    ])
                # Calculates max width for each column
                col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]  
                # Print rows
                for row in rows:
                    line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
                    print(line)
                    if row == headers:
                        print("-+-".join("-" * w for w in col_widths))
            elif menu == 2:
                revenue_per_vehicle = []
                car_ids = set(t[1] for t in global_transactions) # extracting unique car IDs
                for car_id in car_ids:
                    total_revenue = sum(t[3] for t in global_transactions if t[1] == car_id)
                    revenue_per_vehicle.append([car_id, total_revenue])
                revenue_per_vehicle = sorted(revenue_per_vehicle, key=lambda x: x[1], reverse=True)
                # Printing table now
                headers = ["Vehicle ID", "Total Revenue"]
                rows = [headers]
                for i in revenue_per_vehicle:
                    rows.append([
                        str(i[0]),
                        str(i[1]),
                    ])
                # Calculates max width for each column
                col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]  
                # Print rows
                for row in rows:
                    line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
                    print(line)
                    if row == headers:
                        print("-+-".join("-" * w for w in col_widths))
            elif menu == 3:
                maint_per_vehicle = []
                car_ids = set(t[1] for t in global_transactions) # extracting unique car IDs
                for car_id in car_ids:
                    total_maint = sum(t[4] for t in global_transactions if t[1] == car_id)
                    maint_per_vehicle.append([car_id, total_maint])
                maint_per_vehicle = sorted(maint_per_vehicle, key=lambda x: x[1], reverse=True)
                # Printing table now
                headers = ["Vehicle ID", "Total Maintenance"]
                rows = [headers]
                for i in maint_per_vehicle:
                    rows.append([
                        str(i[0]),
                        str(i[1]),
                    ])
                # Calculates max width for each column
                col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]  
                # Print rows
                for row in rows:
                    line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
                    print(line)
                    if row == headers:
                        print("-+-".join("-" * w for w in col_widths))
            elif menu == 4:
                profit_per_vehicle = []
                car_ids = set(t[1] for t in global_transactions) # extracting unique car IDs
                for car_id in car_ids:
                    total_revenue = sum(t[3] for t in global_transactions if t[1] == car_id)
                    total_maintenance = sum(t[4] for t in global_transactions if t[1] == car_id)
                    profit = total_revenue - total_maintenance
                    profit_per_vehicle.append([car_id, profit])
                profit_per_vehicle = sorted(profit_per_vehicle, key=lambda x: x[1], reverse=True)
                # Printing table now
                headers = ["Vehicle ID", "Total Profit"]
                rows = [headers]
                for i in profit_per_vehicle:
                    rows.append([
                        str(i[0]),
                        str(i[1]),
                    ])
                # Calculates max width for each column
                col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]  
                # Print rows
                for row in rows:
                    line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
                    print(line)
                    if row == headers:
                        print("-+-".join("-" * w for w in col_widths))
            elif menu == 5:
                avg_profit_per_rental = []
                car_ids = set(t[1] for t in global_transactions)
                for car_id in car_ids:
                    relevant_txns = [t for t in global_transactions if t[1] == car_id]
                    total_profit = sum(t[3] - t[4] for t in relevant_txns)
                    count = len(relevant_txns)
                    avg_profit = total_profit / count if count > 0 else 0
                    avg_profit_per_rental.append([car_id, avg_profit])
                avg_profit_per_rental = sorted(avg_profit_per_rental, key=lambda x: x[1], reverse=True)
                # Printing table now
                headers = ["Vehicle ID", "Average Profit per Rental Trip"]
                rows = [headers]
                for i in avg_profit_per_rental:
                    rows.append([
                        str(i[0]),
                        str(i[1]),
                    ])
                # Calculates max width for each column
                col_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]  
                # Print rows
                for row in rows:
                    line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
                    print(line)
                    if row == headers:
                        print("-+-".join("-" * w for w in col_widths))
        else:
            return
    return

#__main__
initialise_cars()
while True:
    print ("")
    print ("##############################")
    print ("Share My Car Management System")
    print ("##############################")
    print ("1. View Vehicle Inventory")
    print ("2. Add Vehicle")
    print ("3. Book Vehicle")
    print ("4. Return Vehicle")
    print ("5. View Vehicle Maintenance Logs")
    print ("6. View Transaction Logs")
    print ("7. View Financial Metrics")
    print ("8. Credits")
    print ("9. Exit")
    menu = safe_input("", int)
    if menu == 1:
        show_inventory()
    elif menu == 2:
        add_vehicle()
    elif menu == 3:
        book()
    elif menu == 4:
        return_vehicle()
    elif menu == 5:
        show_maintenance()
    elif menu == 6:
        show_transactions()
    elif menu == 7:
        financial_metrics()
    elif menu == 8:
        print ("")
        print ("All logic created by Kalp Aghada")
        print ("All code written by Kalp Aghada")
        print ("")

    else:
        sys.exit()