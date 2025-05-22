def select_mcb_rating(total_wattage, voltage, load_type):
    # Calculate the total load current
    current = total_wattage / voltage
    
    # Apply a 25% safety margin
    safe_current = current * 1.25
    
    # Determine the MCB type based on load type
    if load_type.lower() == "resistive":
        mcb_type = "B"
    elif load_type.lower() == "inductive":
        mcb_type = "C"
    elif load_type.lower() == "high inrush":
        mcb_type = "D"
    else:
        return "Invalid load type. Please choose from 'resistive', 'inductive', or 'high inrush'."
    
    # Standard MCB ratings
    mcb_ratings = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100]
    
    # Select the nearest standard MCB rating
    for rating in mcb_ratings:
        if safe_current <= rating:
            selected_rating = rating
            break
    else:
        selected_rating = "No suitable MCB rating found. Please consult an electrician."
    
    return f"Suggested MCB Rating: {selected_rating}A, Type: {mcb_type}"

# Example usage
total_wattage = 5000  # Total load in watts
voltage = 230         # Voltage in volts
load_type = "inductive"  # Load type: resistive, inductive, or high inrush

# Get the suggested MCB rating
suggested_mcb = select_mcb_rating(total_wattage, voltage, load_type)
print(suggested_mcb)
