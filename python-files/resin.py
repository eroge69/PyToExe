# Component percentages
percentages = [75, 15, 9.9, 0.1]

# Convert to fraction
fractions = [p / 100 for p in percentages]

# Input total quantity of the formulation (e.g., in kg or liters)
total_quantity = float(input("Enter total formulation quantity: "))

# Input unit cost for each component
unit_costs = []
for i in range(len(fractions)):
    cost = float(input(f"Enter unit cost for component {i+1} (per unit): "))
    unit_costs.append(cost)

# Calculate individual component quantity and cost
total_cost = 0
print("\nComponent Breakdown:")
for i, (fraction, cost_per_unit) in enumerate(zip(fractions, unit_costs)):
    qty = total_quantity * fraction
    cost = qty * cost_per_unit
    total_cost += cost
    print(f"Component {i+1}: {qty:.2f} units x {cost_per_unit:.2f} = {cost:.2f}")

print(f"\nTotal Formulation Cost: {total_cost:.2f}")
print(f"Cost per unit of formulation: {total_cost / total_quantity:.2f}")